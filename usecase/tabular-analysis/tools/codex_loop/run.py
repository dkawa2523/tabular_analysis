#!/usr/bin/env python
"""codex_loop runner (tabular-analysis v5)

This runner is designed to make Codex-driven implementation *reliable* for large refactors.

Key guarantees:
- **No false DONE**: requires BOTH `RESULT: DONE` and the per-task NONCE in the task md.
- **Must-change-globs**: each task must touch at least one path matching `must_change_globs` (default `src/**`).
- **Verification gates**: verification commands are executed (supports fenced blocks AND `- `backticks`` lists).
- **Progress detection**:
  - Uses Git diff/status when inside a git worktree.
  - Falls back to a filesystem snapshot when git is unavailable / not a worktree (prevents 'no progress' dead-ends).

Debugging:
- Logs are written under: `work/runs/task_XXX/`
  - prompt.txt
  - codex_output.txt (+ codex_output_retry.txt if retried)
  - codex_rc.txt
  - verification.txt
  - changed_paths.txt (best effort)

Usage:
  python tools/codex_loop/run.py --repo . --once
  python tools/codex_loop/run.py --repo . --task 3 --once
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

ROOT = pathlib.Path(__file__).resolve().parents[2]  # tabular-analysis root
WORK = ROOT / "work"
QUEUE = WORK / "queue.json"
STATE = WORK / "state.json"
RUNS = WORK / "runs"
RUNS.mkdir(parents=True, exist_ok=True)

IGNORE_PREFIXES = [
    "work/runs/",
    "work/state.json",
]

# snapshot excludes (for non-git fallback)
SNAPSHOT_EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "work/runs",
    "outputs",
    "dist",
    "build",
}
SNAPSHOT_EXCLUDE_PREFIXES = [
    "work/runs/",
]
SNAPSHOT_EXCLUDE_FILES = {
    "work/state.json",
}
SNAPSHOT_MAX_BYTES = 2 * 1024 * 1024  # 2MB; larger files hashed partially

PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


def load_json(p: pathlib.Path, default):
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def save_json(p: pathlib.Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def run(cmd: List[str], cwd: pathlib.Path, input_text: Optional[str] = None, timeout: Optional[int] = None) -> Tuple[int, str, str]:
    p = subprocess.run(
        cmd,
        cwd=str(cwd),
        input=input_text,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    return p.returncode, p.stdout or "", p.stderr or ""


def run_shell(cmd: str, cwd: pathlib.Path) -> Tuple[int, str, str]:
    p = subprocess.run(
        cmd,
        cwd=str(cwd),
        shell=True,
        text=True,
        capture_output=True,
    )
    return p.returncode, p.stdout or "", p.stderr or ""


def is_git_repo(repo: pathlib.Path) -> bool:
    rc, _, _ = run(["git", "rev-parse", "--is-inside-work-tree"], repo)
    return rc == 0


def git_head(repo: pathlib.Path) -> str:
    rc, so, _ = run(["git", "rev-parse", "HEAD"], repo)
    return so.strip() if rc == 0 else ""


def git_porcelain(repo: pathlib.Path) -> List[str]:
    rc, so, _ = run(["git", "status", "--porcelain=v1"], repo)
    if rc != 0:
        return []
    files: List[str] = []
    for line in so.splitlines():
        if not line:
            continue
        if line.startswith("?? "):
            files.append(line[3:].strip())
            continue
        parts = line.split()
        if not parts:
            continue
        path = parts[-1]
        if "->" in line:
            path = line.split("->")[-1].strip()
        files.append(path)
    return files


def diff_hash(repo: pathlib.Path) -> str:
    # tracked + staged diff combined
    rc1, so1, _ = run(["git", "diff", "--no-ext-diff"], repo)
    rc2, so2, _ = run(["git", "diff", "--no-ext-diff", "--cached"], repo)
    blob = (so1 if rc1 == 0 else "") + (so2 if rc2 == 0 else "")
    return hashlib.sha256(blob.encode("utf-8", errors="ignore")).hexdigest()


def should_ignore(path: str) -> bool:
    for pref in IGNORE_PREFIXES:
        if path.startswith(pref):
            return True
    return False


def filter_ignored(paths: List[str]) -> List[str]:
    return [p for p in paths if not should_ignore(p)]


def match_any_glob(path: str, globs: List[str]) -> bool:
    # globs are like "src/**"
    for g in globs:
        if fnmatch.fnmatch(path, g) or fnmatch.fnmatch(path, g.replace("**", "*")):
            return True
        # also try pathlib match semantics
        try:
            if pathlib.PurePosixPath(path).match(g):
                return True
        except Exception:
            pass
    return False


def snapshot_index(repo: pathlib.Path) -> Dict[str, str]:
    """Best-effort content snapshot for non-git environments."""
    idx: Dict[str, str] = {}
    for p in repo.rglob("*"):
        if p.is_dir():
            # skip excluded dirs
            rel_dir = p.relative_to(repo).as_posix()
            parts = rel_dir.split("/")
            if parts and parts[0] in SNAPSHOT_EXCLUDE_DIRS:
                # prune by skipping walking; rglob doesn't allow prune, so just continue
                continue
            continue
        if not p.is_file():
            continue
        rel = p.relative_to(repo).as_posix()
        if rel in SNAPSHOT_EXCLUDE_FILES:
            continue
        if any(rel.startswith(pref) for pref in SNAPSHOT_EXCLUDE_PREFIXES):
            continue
        # skip top-level excluded dirs
        top = rel.split("/")[0]
        if top in SNAPSHOT_EXCLUDE_DIRS:
            continue
        try:
            st = p.stat()
        except Exception:
            continue
        h = hashlib.sha256()
        h.update(rel.encode("utf-8"))
        # hash content (partial for large files)
        try:
            with p.open("rb") as f:
                if st.st_size <= SNAPSHOT_MAX_BYTES:
                    data = f.read()
                    h.update(data)
                else:
                    # read first and last chunks
                    head = f.read(256 * 1024)
                    h.update(head)
                    try:
                        f.seek(max(0, st.st_size - 256 * 1024))
                        tail = f.read(256 * 1024)
                        h.update(tail)
                    except Exception:
                        pass
        except Exception:
            # if cannot read, hash metadata only
            h.update(str(st.st_size).encode("utf-8"))
            h.update(str(int(st.st_mtime)).encode("utf-8"))
        idx[rel] = h.hexdigest()
    return idx


def snapshot_changed_paths(before: Dict[str, str], after: Dict[str, str]) -> List[str]:
    keys = set(before.keys()) | set(after.keys())
    changed = [k for k in keys if before.get(k) != after.get(k)]
    return sorted(changed)


def extract_verification(task_md: str) -> List[str]:
    """Extract verification commands.

    Supports:
    - Fenced blocks after '## Verification' (preferred)
    - Backtick list items like: - `python -m ...`
    """
    m = re.search(r"^##\s+Verification\s*$", task_md, flags=re.M)
    if not m:
        return []
    tail = task_md[m.end():]
    # stop at next heading
    tail = re.split(r"^##\s+", tail, maxsplit=1, flags=re.M)[0]

    # 1) fenced block
    blocks = re.findall(r"```(?:bash|sh)?\s*\n(.*?)\n```", tail, flags=re.S)
    cmds: List[str] = []
    if blocks:
        for line in blocks[0].splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            cmds.append(line)
        return cmds

    # 2) list items with backticks
    for line in tail.splitlines():
        line = line.strip()
        m2 = re.match(r"^[-*]\s+`(.+?)`\s*$", line)
        if m2:
            cmds.append(m2.group(1).strip())
    return cmds


def verify(repo: pathlib.Path, task_md: str) -> Tuple[bool, str]:
    cmds = extract_verification(task_md)
    out: List[str] = []
    if not cmds:
        return True, "(no verification commands found)"
    ok = True
    for c in cmds:
        out.append(f"$ {c}")
        rc, so, se = run_shell(c, repo)
        if so.strip():
            out.append(so.strip())
        if se.strip():
            out.append(se.strip())
        if rc != 0:
            ok = False
            out.append(f"(FAILED rc={rc})")
            break
    return ok, "\n".join(out)


def codex_caps(repo: pathlib.Path) -> Dict[str, bool]:
    rc, so, se = run(["codex", "exec", "--help"], repo)
    txt = (so or "") + (se or "")
    return {
        "has_sandbox": "--sandbox" in txt or "-s" in txt,
        "has_full_auto": "--full-auto" in txt,
        "has_skip_git": "--skip-git-repo-check" in txt,
    }


def call_codex(repo: pathlib.Path, prompt: str, caps: Dict[str, bool], force_skip_git: bool) -> Tuple[int, str]:
    cmd = ["codex", "exec"]
    if caps.get("has_sandbox", True):
        cmd += ["--sandbox", "workspace-write"]
    if caps.get("has_full_auto", False):
        cmd += ["--full-auto"]
    if force_skip_git and caps.get("has_skip_git", False):
        cmd += ["--skip-git-repo-check"]
    cmd += ["-"]  # read prompt from stdin
    rc, so, se = run(cmd, repo, input_text=prompt)
    out = (so or "") + ("\n" + se if se else "")
    return rc, out


def safe_read(p: pathlib.Path, limit: int = 20000) -> str:
    if not p.exists():
        try:
            return f"(missing: {p.relative_to(ROOT)})"
        except Exception:
            return f"(missing: {p})"
    txt = p.read_text(encoding="utf-8", errors="ignore")
    if len(txt) > limit:
        return txt[:limit] + "\n...(truncated)..."
    return txt


def platform_scan(repo: pathlib.Path) -> str:
    scan = repo / "tools" / "platform_scan.py"
    if not scan.exists():
        return "(platform_scan.py missing)"
    rc, so, se = run(["python", str(scan)], repo)
    txt = (so or "") + ("\n" + se if se else "")
    lines = txt.splitlines()
    if len(lines) > 250:
        lines = lines[-250:]
        txt = "\n".join(lines)
    return txt


def build_prompt(task: Dict[str, Any], nonce: str, last_failure: str, platform_info: str) -> str:
    agents = safe_read(ROOT / "AGENTS.md", 16000)
    task_md = safe_read(ROOT / task["path"], 22000)

    contract_text: List[str] = []
    for c in task.get("contracts") or []:
        contract_text.append(f"\n\n# CONTRACT: {c}\n" + safe_read(ROOT / c, 12000))

    # include skill texts (lightweight)
    skill_text: List[str] = []
    skills_root = ROOT / "agentskills" / "skills"
    for sid in task.get("skills") or []:
        cand = list(skills_root.glob(f"{sid}*.md"))
        if cand:
            rel = cand[0].relative_to(ROOT)
            skill_text.append(f"\n\n# SKILL: {sid} ({rel})\n" + safe_read(ROOT / rel, 12000))

    must_globs = task.get("must_change_globs", ["src/**"])

    return f"""あなたはこのリポジトリの実装担当です。以下を厳守してください。

- **独立タスク設計**: preprocess/train/infer/leaderboard は親子タスクにしない
- **HyperParameters はそのタスクの入力設定だけ**（full config connect禁止）
- **ローカルファースト**: ClearML off で必ず動作確認→その後 ClearML on
- **registry が拡張点**: 新しい前処理/モデル/指標/可視化は registry / viz / conf/group に集約
- **platform再利用**: 同等機能を新規実装する前に platform を探索し再利用
- **ファイル増殖禁止**: 追加ファイルは必要最小限
- **タスクは中途半端で次へ進まない**: 完了したら task md に RESULT: DONE を書く
- **誤DONE防止**: task md に NONCE を貼ること（下記）
- **重要**: 変更が必要です。**必ず** must-change-globs にマッチするファイルを変更し、task md も更新してください。

AUTOMATION NONCE (task md の RESULT に貼り付け必須): {nonce}
Must-change-globs (必ず変更する): {must_globs}

--- LAST FAILURE (if any) ---
{last_failure}

--- PLATFORM SCAN (summary) ---
{platform_info}

# AGENTS
{agents}

# TASK
{task_md}

{''.join(contract_text)}

{''.join(skill_text)}

# OUTPUT REQUIREMENTS
- 必ずリポジトリのファイルを編集して変更をコミット前の状態に残してください（git commit は不要）
- 必ず task md の RESULT に NONCE と RESULT: DONE を書き、Evidence/Verification/Next Improvements を埋めてください
"""


def pick_next(queue: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    def eligible(t):
        return t.get("status") in ("todo", "doing")

    cand = [t for t in queue if eligible(t)]
    if not cand:
        return None
    cand.sort(key=lambda x: (PRIORITY_ORDER.get(x.get("priority", "P9"), 9), int(x.get("id", 9999))))
    return cand[0]


def print_failure(task_id: int, reason: str, task_run: pathlib.Path) -> None:
    print(f"Task {task_id} FAILED: {reason}")
    print(f"  Logs: {task_run}")
    print(f"   - prompt: {task_run / 'prompt.txt'}")
    print(f"   - codex:  {task_run / 'codex_output.txt'}")
    if (task_run / 'codex_output_retry.txt').exists():
        print(f"   - codex_retry:  {task_run / 'codex_output_retry.txt'}")
    print(f"   - rc:    {task_run / 'codex_rc.txt'}")
    print(f"   - verify:{task_run / 'verification.txt'}")
    if (task_run / 'changed_paths.txt').exists():
        print(f"   - changed:{task_run / 'changed_paths.txt'}")


def tail(text: str, n: int = 1200) -> str:
    if len(text) <= n:
        return text
    return text[-n:]


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--task", type=int, default=None)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)

    repo = pathlib.Path(args.repo).resolve()
    if not (repo / "work" / "queue.json").exists():
        print(f"ERROR: expected to run inside tabular-analysis root. Missing: {repo/'work/queue.json'}", file=sys.stderr)
        return 2

    if shutil.which("codex") is None:
        print("ERROR: codex not found in PATH", file=sys.stderr)
        return 3

    git_mode = is_git_repo(repo)
    if not git_mode:
        print("WARN: not inside a git worktree (or git unavailable). Using filesystem snapshot for progress detection.")
        print("      If this is unintended, run this inside a git clone or run `git init` at the repo root.")

    caps = codex_caps(repo)
    save_json(RUNS / "_codex_caps.json", caps)

    state = load_json(STATE, default={"task_nonces": {}, "last_failure": ""})
    task_nonces: Dict[str, str] = state.get("task_nonces") or {}
    last_failure: str = state.get("last_failure") or ""

    while True:
        queue = load_json(QUEUE, default=[])
        if args.task is not None:
            t = next((x for x in queue if int(x.get("id")) == args.task), None)
        else:
            t = pick_next(queue)

        if not t:
            print("No eligible tasks found. (All done or blocked)")
            return 0

        # set doing
        if t.get("status") == "todo":
            for i, x in enumerate(queue):
                if int(x.get("id")) == int(t.get("id")):
                    queue[i]["status"] = "doing"
            save_json(QUEUE, queue)

        # stable nonce
        tid = str(int(t["id"]))
        if tid not in task_nonces:
            task_nonces[tid] = uuid.uuid4().hex
            save_json(STATE, {"task_nonces": task_nonces, "last_failure": last_failure})
        nonce = task_nonces[tid]

        # platform scan
        pinfo = platform_scan(repo)

        prompt = build_prompt(t, nonce, last_failure, pinfo)
        task_run = RUNS / f"task_{int(t['id']):03d}"
        task_run.mkdir(parents=True, exist_ok=True)
        (task_run / "prompt.txt").write_text(prompt, encoding="utf-8")

        # capture before
        before_head = git_head(repo) if git_mode else ""
        before_files = filter_ignored(git_porcelain(repo)) if git_mode else []
        before_diff = diff_hash(repo) if git_mode else ""
        before_snap = snapshot_index(repo) if not git_mode else {}

        # call codex (retry with skip-git if trusted-dir error)
        rc, out = call_codex(repo, prompt, caps, force_skip_git=False)
        if ("Not inside a trusted directory" in out) and caps.get("has_skip_git", False):
            rc2, out2 = call_codex(repo, prompt, caps, force_skip_git=True)
            if rc2 == 0:
                rc, out = rc2, out2

        (task_run / "codex_output.txt").write_text(out, encoding="utf-8")
        (task_run / "codex_rc.txt").write_text(str(rc), encoding="utf-8")

        # capture after
        after_head = git_head(repo) if git_mode else ""
        after_files = filter_ignored(git_porcelain(repo)) if git_mode else []
        after_diff = diff_hash(repo) if git_mode else ""
        after_snap = snapshot_index(repo) if not git_mode else {}

        # progress + changed paths
        changed_paths: List[str] = []
        progress = False
        if git_mode:
            progress = (after_files != before_files) or (after_diff != before_diff) or (after_head != before_head)
            # best effort changed paths: include status paths + (if head changed) commit diff
            changed_paths = sorted(set(after_files))
            if after_head and before_head and after_head != before_head:
                rc3, so3, _ = run(["git", "diff", "--name-only", f"{before_head}..{after_head}"], repo)
                if rc3 == 0:
                    changed_paths = sorted(set(changed_paths) | set([x.strip() for x in so3.splitlines() if x.strip()]))
        else:
            progress = after_snap != before_snap
            changed_paths = snapshot_changed_paths(before_snap, after_snap)

        (task_run / "changed_paths.txt").write_text("\n".join(changed_paths), encoding="utf-8")

        # read task md
        task_md_path = repo / t["path"]
        task_md_text = task_md_path.read_text(encoding="utf-8", errors="ignore") if task_md_path.exists() else ""

        must_globs = t.get("must_change_globs", ["src/**"])
        touched_glob = any(match_any_glob(p, must_globs) for p in changed_paths)

        nonce_ok = nonce in task_md_text
        done_ok = "RESULT: DONE" in task_md_text

        ok_verify, vout = verify(repo, task_md_text)
        (task_run / "verification.txt").write_text(vout, encoding="utf-8")

        # failures
        if rc != 0:
            last_failure = f"codex rc={rc}\n---\n{tail(out, 2000)}"
            save_json(STATE, {"task_nonces": task_nonces, "last_failure": last_failure})
            print_failure(int(t["id"]), f"codex failed rc={rc}", task_run)
            if args.once:
                return 10
            time.sleep(0.2)
            continue

        # If no progress, automatically retry once with a stronger instruction (common when Codex answers but doesn't edit).
        if not progress:
            retry_prompt = prompt + "\n\n# NO-PROGRESS RETRY\n前回の実行ではファイル差分が検出できませんでした。\n**必ず** must-change-globs に一致するファイルを編集し、task md に NONCE と RESULT: DONE を書いてください。\n"
            rc_r, out_r = call_codex(repo, retry_prompt, caps, force_skip_git=False)
            (task_run / "codex_output_retry.txt").write_text(out_r, encoding="utf-8")
            # refresh after
            after_head2 = git_head(repo) if git_mode else ""
            after_files2 = filter_ignored(git_porcelain(repo)) if git_mode else []
            after_diff2 = diff_hash(repo) if git_mode else ""
            after_snap2 = snapshot_index(repo) if not git_mode else {}
            if git_mode:
                progress = (after_files2 != before_files) or (after_diff2 != before_diff) or (after_head2 != before_head)
                changed_paths = sorted(set(after_files2))
                if after_head2 and before_head and after_head2 != before_head:
                    rc3, so3, _ = run(["git", "diff", "--name-only", f"{before_head}..{after_head2}"], repo)
                    if rc3 == 0:
                        changed_paths = sorted(set(changed_paths) | set([x.strip() for x in so3.splitlines() if x.strip()]))
            else:
                progress = after_snap2 != before_snap
                changed_paths = snapshot_changed_paths(before_snap, after_snap2)

            (task_run / "changed_paths.txt").write_text("\n".join(changed_paths), encoding="utf-8")

            # reload task md after retry
            task_md_text = task_md_path.read_text(encoding="utf-8", errors="ignore") if task_md_path.exists() else ""
            touched_glob = any(match_any_glob(p, must_globs) for p in changed_paths)
            nonce_ok = nonce in task_md_text
            done_ok = "RESULT: DONE" in task_md_text
            ok_verify, vout = verify(repo, task_md_text)
            (task_run / "verification.txt").write_text(vout, encoding="utf-8")

            if not progress:
                last_failure = "no progress detected (git diff empty / snapshot unchanged)\n---\n" + tail(out_r or out, 1500)
                save_json(STATE, {"task_nonces": task_nonces, "last_failure": last_failure})
                print_failure(int(t["id"]), "no progress detected", task_run)
                if args.once:
                    return 11
                time.sleep(0.2)
                continue

        if not touched_glob:
            last_failure = f"must_change_globs not satisfied: {must_globs}\nchanged_paths_sample={changed_paths[:20]}"
            save_json(STATE, {"task_nonces": task_nonces, "last_failure": last_failure})
            print_failure(int(t["id"]), "must_change_globs not satisfied", task_run)
            if args.once:
                return 12
            time.sleep(0.2)
            continue

        if not nonce_ok:
            last_failure = "NONCE missing in task md RESULT section"
            save_json(STATE, {"task_nonces": task_nonces, "last_failure": last_failure})
            print_failure(int(t["id"]), "NONCE missing", task_run)
            if args.once:
                return 13
            time.sleep(0.2)
            continue

        if not done_ok:
            last_failure = "RESULT: DONE missing in task md"
            save_json(STATE, {"task_nonces": task_nonces, "last_failure": last_failure})
            print_failure(int(t["id"]), "RESULT: DONE missing", task_run)
            if args.once:
                return 14
            time.sleep(0.2)
            continue

        if not ok_verify:
            last_failure = f"verification failed\n---\n{tail(vout, 2000)}"
            save_json(STATE, {"task_nonces": task_nonces, "last_failure": last_failure})
            print_failure(int(t["id"]), "verification failed", task_run)
            if args.once:
                return 15
            time.sleep(0.2)
            continue

        # mark done
        for i, x in enumerate(queue):
            if int(x.get("id")) == int(t.get("id")):
                queue[i]["status"] = "done"
        save_json(QUEUE, queue)
        last_failure = ""
        save_json(STATE, {"task_nonces": task_nonces, "last_failure": last_failure})
        print(f"Task {t['id']} DONE")
        if args.once:
            return 0
        time.sleep(0.2)


if __name__ == "__main__":
    raise SystemExit(main())
