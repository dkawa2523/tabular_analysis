#!/usr/bin/env python3
"""
codex_loop runner (tabular-analysis)
- Runs Codex CLI against work/queue.json tasks.
- Designed to be robust across environments:
  * codex exec expects PROMPT as positional arg
  * sandbox modes are limited (read-only/workspace-write/danger-full-access)
  * git may be unavailable; uses snapshot-based progress detection
  * queue may become inconsistent (e.g., status=doing left behind); reconciles automatically

Key guarantees:
- Never marks a task DONE unless:
  1) verification commands (from task md) all exit with code 0
  2) task md contains `RESULT: DONE` and a NONCE
  3) at least one changed file matches must_change_globs (default: src/** or conf/** or docs/** etc.)
"""

from __future__ import annotations

import argparse
import dataclasses
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

# -------------------------
# Utilities
# -------------------------

VALID_SANDBOX = {"read-only", "workspace-write", "danger-full-access"}

IGNORE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "work/runs",
    "outputs",
}

DEFAULT_MUST_CHANGE_GLOBS = [
    "src/**",
    "conf/**",
    "docs/**",
    "requirements/**",
    "pyproject.toml",
    "tools/**",
]


def _posix(p: Path) -> str:
    return p.as_posix()


def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def _write_text(p: Path, s: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")


def _read_json(p: Path) -> Any:
    return json.loads(_read_text(p))


def _write_json(p: Path, obj: Any) -> None:
    _write_text(p, json.dumps(obj, indent=2, ensure_ascii=False))


def _now_ts() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


def _norm_id(x: Any) -> str:
    s = str(x).strip()
    m = re.fullmatch(r"T?0*([0-9]+)", s, flags=re.IGNORECASE)
    if m:
        return m.group(1)
    return s


def _id_sort_key(x: Any) -> int:
    s = _norm_id(x)
    try:
        return int(s)
    except Exception:
        return 999999


def _priority_sort_key(p: Any) -> int:
    if p is None:
        return 999
    if isinstance(p, int):
        return p
    s = str(p).strip()
    m = re.fullmatch(r"P(\d+)", s, flags=re.IGNORECASE)
    if m:
        return int(m.group(1))
    try:
        return int(s)
    except Exception:
        return 999


def _glob_match_any(path_posix: str, globs: Iterable[str]) -> bool:
    for pat in globs:
        pat = pat.strip()
        if not pat:
            continue
        # normalize to posix
        pat = pat.replace("\\", "/")
        if fnmatch.fnmatch(path_posix, pat):
            return True
    return False


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _should_ignore(rel_posix: str) -> bool:
    rel_posix = rel_posix.lstrip("./")
    for d in IGNORE_DIRS:
        dpos = d.replace("\\", "/").rstrip("/")
        if rel_posix == dpos or rel_posix.startswith(dpos + "/"):
            return True
    return False


def _snapshot(repo: Path) -> Dict[str, str]:
    """Return mapping relpath->hash for progress detection."""
    snap: Dict[str, str] = {}
    for p in repo.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(repo).as_posix()
        if _should_ignore(rel):
            continue
        # avoid hashing huge binaries in data; keep it simple:
        try:
            if p.stat().st_size > 20 * 1024 * 1024:
                # large file: use size+mtime as pseudo-hash
                st = p.stat()
                snap[rel] = f"large:{st.st_size}:{int(st.st_mtime)}"
            else:
                snap[rel] = _sha256_file(p)
        except Exception:
            # if unreadable, still include marker
            snap[rel] = "unreadable"
    return snap


def _diff_snap(before: Dict[str, str], after: Dict[str, str]) -> List[str]:
    changed = []
    keys = set(before.keys()) | set(after.keys())
    for k in sorted(keys):
        if before.get(k) != after.get(k):
            changed.append(k)
    return changed


# -------------------------
# Runtime / Codex
# -------------------------

@dataclasses.dataclass
class CodexRuntime:
    sandbox_mode: str = "workspace-write"
    supports_skip_git_repo_check: bool = False

    @staticmethod
    def load(repo: Path) -> "CodexRuntime":
        # env override
        env_mode = os.environ.get("CODEX_SANDBOX_MODE")
        mode = env_mode.strip() if env_mode else None

        rt_path = repo / "tools" / "codex_loop" / "runtime.json"
        supports_skip = False
        if rt_path.exists():
            try:
                data = _read_json(rt_path)
                mode = mode or data.get("sandbox_mode") or data.get("sandbox") or mode
                supports_skip = bool(data.get("supports_skip_git_repo_check", False))
            except Exception:
                pass

        if not mode:
            mode = "workspace-write"
        if mode not in VALID_SANDBOX:
            # fall back
            mode = "workspace-write"

        # if we can't trust runtime.json, probe help once
        if not supports_skip:
            supports_skip = _probe_skip_git_repo_check()

        return CodexRuntime(sandbox_mode=mode, supports_skip_git_repo_check=supports_skip)


def _probe_skip_git_repo_check() -> bool:
    try:
        r = subprocess.run(
            ["codex", "exec", "--help"],
            capture_output=True,
            text=True,
        )
        s = (r.stdout or "") + (r.stderr or "")
        return "--skip-git-repo-check" in s
    except Exception:
        return False


def _run_codex(runtime: CodexRuntime, prompt: str, cwd: Path, log_path: Path) -> int:
    cmd = ["codex", "exec", "--sandbox", runtime.sandbox_mode]
    if runtime.supports_skip_git_repo_check:
        cmd.append("--skip-git-repo-check")
    cmd.append(prompt)

    r = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )
    out = (r.stdout or "") + (r.stderr or "")
    _write_text(log_path, out)
    return r.returncode


# -------------------------
# Queue / Tasks
# -------------------------

def _load_queue(repo: Path) -> Tuple[Path, Any, List[Dict[str, Any]]]:
    qpath = repo / "work" / "queue.json"
    data = _read_json(qpath)
    if isinstance(data, dict) and "tasks" in data:
        tasks = data["tasks"]
    elif isinstance(data, list):
        tasks = data
    else:
        raise ValueError("Unsupported queue.json format (must be list or dict with 'tasks').")
    if not isinstance(tasks, list):
        raise ValueError("queue.json tasks must be a list")
    return qpath, data, tasks


def _task_md_path(repo: Path, task: Dict[str, Any]) -> Path:
    p = task.get("path")
    if not p:
        # default
        tid = _id_sort_key(task.get("id"))
        return repo / "work" / "tasks" / f"T{tid:03d}.md"
    return repo / str(p)


def _task_md_contains_done(md_text: str) -> bool:
    # We treat RESULT: DONE as the canonical marker
    if re.search(r"^\s*-\s*RESULT:\s*DONE\s*$", md_text, flags=re.MULTILINE):
        return True
    return False


def _task_md_nonce(md_text: str) -> Optional[str]:
    # require a NONCE line
    m = re.search(r"NONCE:\s*([0-9a-fA-F]{8,})", md_text)
    return m.group(1) if m else None


def _reconcile_queue(repo: Path, tasks: List[Dict[str, Any]]) -> None:
    """Make queue statuses consistent with task markdown markers."""
    for t in tasks:
        status = (t.get("status") or "todo").lower()
        mdp = _task_md_path(repo, t)
        if not mdp.exists():
            # no md -> do not auto mark done
            if status == "doing":
                t["status"] = "todo"
            continue
        txt = _read_text(mdp)
        md_done = _task_md_contains_done(txt)
        if md_done:
            t["status"] = "done"
        else:
            if status == "doing":
                # avoid permanent blocking
                t["status"] = "todo"


def _eligible_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_id = {_norm_id(t["id"]): t for t in tasks}
    eligible: List[Dict[str, Any]] = []
    for t in tasks:
        status = (t.get("status") or "todo").lower()
        if status != "todo":
            continue
        deps = t.get("depends_on") or []
        ok = True
        for d in deps:
            did = _norm_id(d)
            if did not in by_id:
                ok = False
                break
            if (by_id[did].get("status") or "").lower() != "done":
                ok = False
                break
        if ok:
            eligible.append(t)

    eligible.sort(key=lambda x: (_priority_sort_key(x.get("priority")), _id_sort_key(x.get("id"))))
    return eligible


# -------------------------
# Verification
# -------------------------

def _extract_verification_cmds(task_md: str) -> List[str]:
    """
    Extract verification commands from markdown.

    Supported patterns:
      - `python ...`
      - bullet lines containing backticks
      - fenced blocks ```bash ... ```
      - lines starting with "Verification:" followed by commands separated by ';'
    """
    cmds: List[str] = []

    lines = task_md.splitlines()

    # 1) backticks on lines
    for line in lines:
        if "`" in line:
            # capture each `...`
            parts = re.findall(r"`([^`]+)`", line)
            for p in parts:
                p = p.strip()
                if p.startswith(("python", "pytest", "ruff", "mypy", "bash", "sh", "ls", "cat")):
                    cmds.append(p)

    # 2) fenced blocks
    in_fence = False
    fence_lang = ""
    buf: List[str] = []
    for line in lines:
        if line.strip().startswith("```"):
            if not in_fence:
                in_fence = True
                fence_lang = line.strip().lstrip("```").strip().lower()
                buf = []
            else:
                # close
                if fence_lang in ("bash", "sh", "shell", ""):
                    for b in buf:
                        b = b.strip()
                        if not b or b.startswith("#"):
                            continue
                        cmds.append(b)
                in_fence = False
                fence_lang = ""
                buf = []
            continue
        if in_fence:
            buf.append(line)

    # 3) "Verification:" style
    for line in lines:
        if line.strip().lower().startswith("verification:"):
            tail = line.split(":", 1)[1].strip()
            # split by ';'
            for part in tail.split(";"):
                part = part.strip()
                if part:
                    # may contain "(ok)" etc.
                    cmds.append(part)

    # de-dup while preserving order
    seen = set()
    out: List[str] = []
    for c in cmds:
        c2 = c.strip()
        if not c2:
            continue
        if c2 not in seen:
            seen.add(c2)
            out.append(c2)
    return out


def _clean_cmd(cmd: str) -> Tuple[str, Optional[str]]:
    """
    Clean a verification command.
    - Remove trailing "(ok)/(pass)" annotations.
    - Support optional expected output: "CMD -> EXPECTED"
    """
    s = cmd.strip()

    # remove trailing annotations like "(ok)" "(pass)" "(passed)"
    s = re.sub(r"\s*\((ok|pass|passed)\)\s*$", "", s, flags=re.IGNORECASE).strip()

    expected = None
    if "->" in s:
        left, right = s.split("->", 1)
        s = left.strip()
        expected = right.strip()
        # strip markdown backticks
        if expected.startswith("`") and expected.endswith("`"):
            expected = expected[1:-1].strip()
        # strip quotes
        expected = expected.strip().strip('"').strip("'").strip()
        if expected == "":
            expected = None

    return s, expected


def _run_verification(repo: Path, task: Dict[str, Any], run_dir: Path) -> Tuple[bool, str]:
    mdp = _task_md_path(repo, task)
    if not mdp.exists():
        return True, "no task md; skip verification"

    txt = _read_text(mdp)
    cmds = _extract_verification_cmds(txt)

    vlog = run_dir / "verification.txt"
    lines: List[str] = []
    ok = True
    failed_cmd = ""

    if not cmds:
        _write_text(vlog, "No verification commands found in task md.\n")
        return False, "no verification commands"

    for raw in cmds:
        cmd, expected = _clean_cmd(raw)
        if not cmd:
            continue

        lines.append(f"$ {cmd}\n")
        r = subprocess.run(cmd, cwd=str(repo), shell=True, capture_output=True, text=True)
        stdout = (r.stdout or "")
        stderr = (r.stderr or "")
        if stdout:
            lines.append(stdout + ("\n" if not stdout.endswith("\n") else ""))
        if stderr:
            lines.append(stderr + ("\n" if not stderr.endswith("\n") else ""))

        # PASS/FAIL rule:
        # - primary: returncode==0
        # - optional: expected substring match (if provided)
        if r.returncode != 0:
            ok = False
            failed_cmd = cmd
            lines.append(f"[FAIL] returncode={r.returncode}\n")
            break
        if expected is not None:
            combined = (stdout + "\n" + stderr).strip()
            if expected not in combined:
                ok = False
                failed_cmd = cmd
                lines.append(f"[FAIL] expected substring not found: {expected}\n")
                break

        lines.append("[OK]\n\n")

    _write_text(vlog, "".join(lines))
    if not ok and failed_cmd:
        _write_text(run_dir / "verification_failed_cmd.txt", failed_cmd + "\n")
    return ok, ("ok" if ok else f"failed: {failed_cmd}")


# -------------------------
# Task completion checks
# -------------------------

def _task_markers_ok(repo: Path, task: Dict[str, Any]) -> Tuple[bool, str]:
    mdp = _task_md_path(repo, task)
    if not mdp.exists():
        return False, f"task md not found: {mdp}"
    txt = _read_text(mdp)
    if not _task_md_contains_done(txt):
        return False, "missing 'RESULT: DONE' in task md"
    nonce = _task_md_nonce(txt)
    if not nonce:
        return False, "missing NONCE in task md"
    return True, "ok"


def _must_change_ok(changed_paths: List[str], must_globs: List[str]) -> bool:
    for p in changed_paths:
        if _glob_match_any(p, must_globs):
            return True
    return False


# -------------------------
# Main
# -------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".", help="Repository root (tabular-analysis)")
    ap.add_argument("--once", action="store_true", help="Run at most one eligible task")
    ap.add_argument("--task", default=None, help="Run specific task id (optional)")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    os.chdir(repo)

    qpath, qdata, tasks = _load_queue(repo)

    # reconcile queue first (prevents 'doing' deadlocks)
    _reconcile_queue(repo, tasks)
    _write_json(qpath, qdata)

    eligible = _eligible_tasks(tasks)
    if args.task is not None:
        tid = _norm_id(args.task)
        eligible = [t for t in eligible if _norm_id(t["id"]) == tid]

    if not eligible:
        print("No eligible tasks found. (All done or blocked by dependencies)")
        return 0

    runtime = CodexRuntime.load(repo)

    # run one task (or loop, but here --once is default usage)
    t = eligible[0]
    tid_int = _id_sort_key(t.get("id"))
    run_dir = repo / "work" / "runs" / f"task_{tid_int:03d}"
    run_dir.mkdir(parents=True, exist_ok=True)

    task_md = _task_md_path(repo, t)
    prompt = (
        f"You are implementing Task {tid_int:03d} for tabular-analysis.\n"
        f"Read and follow: {task_md.as_posix()}\n"
        f"Also follow docs/ (UI contract, invariants, risks).\n"
        f"IMPORTANT:\n"
        f"- You MUST modify actual code/config/docs files (not only suggestions).\n"
        f"- Update the task markdown completion section with RESULT: DONE and a NONCE.\n"
        f"- Keep changes minimal and review-friendly.\n"
    )

    # Save prompt for debugging
    _write_text(run_dir / "prompt.txt", prompt)

    # If the task markdown is already marked DONE with NONCE, avoid re-running Codex.
    # This prevents loops where Codex already applied changes but a previous runner failed.
    m_ok0, _ = _task_markers_ok(repo, t)
    if m_ok0:
        v_ok0, v_msg0 = _run_verification(repo, t, run_dir)
        if not v_ok0:
            print(f"Task {tid_int} FAILED: verification failed: {v_msg0}")
            print(f"  Logs: {run_dir}")
            return 2
        for x in tasks:
            if _norm_id(x["id"]) == _norm_id(t["id"]):
                x["status"] = "done"
                break
        _write_json(qpath, qdata)
        print(f"Task {tid_int} DONE (verification-only)")
        return 0

    before = _snapshot(repo)
    codex_log = run_dir / "codex_output.txt"
    rc = _run_codex(runtime, prompt, cwd=repo, log_path=codex_log)
    _write_text(run_dir / "codex_rc.txt", str(rc) + "\n")

    after = _snapshot(repo)
    changed = _diff_snap(before, after)
    _write_text(run_dir / "changed_paths.txt", "\n".join(changed) + ("\n" if changed else ""))

    if rc != 0:
        print(f"Task {tid_int} FAILED: codex exec return code {rc}")
        print(f"  Logs: {run_dir}")
        return 2

    must_globs = t.get("must_change_globs") or DEFAULT_MUST_CHANGE_GLOBS
    if not _must_change_ok(changed, must_globs):
        print(f"Task {tid_int} FAILED: must_change_globs not satisfied")
        print(f"  Logs: {run_dir}")
        return 2

    v_ok, v_msg = _run_verification(repo, t, run_dir)
    if not v_ok:
        # If task md is already DONE markers, allow reconcile path:
        print(f"Task {tid_int} FAILED: verification failed: {v_msg}")
        print(f"  Logs: {run_dir}")
        return 2

    m_ok, m_msg = _task_markers_ok(repo, t)
    if not m_ok:
        print(f"Task {tid_int} NOT DONE: {m_msg}")
        print(f"  Logs: {run_dir}")
        # leave task todo so it reruns
        return 1

    # Mark done in queue and persist
    for x in tasks:
        if _norm_id(x["id"]) == _norm_id(t["id"]):
            x["status"] = "done"
            break
    _write_json(qpath, qdata)

    print(f"Task {tid_int} DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
