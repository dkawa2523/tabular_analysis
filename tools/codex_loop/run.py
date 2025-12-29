#!/usr/bin/env python
import argparse, json, pathlib, subprocess, sys, time, shutil, re, fnmatch, uuid, hashlib
from typing import List, Dict, Any, Optional, Tuple

RUNNER_VERSION = "polyrepo-scaffold-v1"

PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}

DEFAULT_IGNORE_PATHS = [
    "work/queue.json",
    "work/_runner_state.json",
    "work/runs/",
]

def load_json(p: pathlib.Path, default=None):
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))

def save_json(p: pathlib.Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def run(cmd: List[str], cwd: pathlib.Path, input_text: Optional[str]=None) -> Tuple[int,str,str]:
    p = subprocess.run(cmd, cwd=cwd, text=True, input=input_text, capture_output=True)
    return p.returncode, p.stdout, p.stderr

def run_shell(cmd: str, cwd: pathlib.Path) -> Tuple[int, str, str]:
    p = subprocess.run(["bash", "-lc", cmd], cwd=cwd, text=True, capture_output=True)
    return p.returncode, p.stdout, p.stderr

def git_porcelain(repo: pathlib.Path) -> Tuple[int, str, str]:
    return run(["git", "status", "--porcelain=v1"], repo)

def parse_dirty_files(porcelain: str) -> List[str]:
    files: List[str] = []
    for line in porcelain.splitlines():
        if not line:
            continue
        if line.startswith("?? "):
            files.append(line[3:].strip()); continue
        m = re.match(r"^[ MADRCU?!]{2}\s+(.*)$", line)
        if not m:
            continue
        path = m.group(1).strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        files.append(path)
    return files

def should_ignore(path: str, ignore_paths: List[str]) -> bool:
    for ign in ignore_paths:
        if ign.endswith("/"):
            if path.startswith(ign): return True
        else:
            if path == ign: return True
    return False

def filter_ignored(files: List[str], ignore_paths: List[str]) -> List[str]:
    return [f for f in files if not should_ignore(f, ignore_paths)]

def match_any_glob(path: str, globs: List[str]) -> bool:
    for g in globs:
        if fnmatch.fnmatch(path, g) or fnmatch.fnmatch(path, g.replace("**/", "")):
            return True
    return False

def extract_verification_commands(task_md: str) -> List[str]:
    m = re.search(r"^##\s+Verification\s*$", task_md, flags=re.MULTILINE)
    if not m:
        return []
    tail = task_md[m.end():]
    blocks = re.findall(r"```(?:bash|sh|zsh)?\s*\n(.*?)\n```", tail, flags=re.DOTALL)
    if not blocks:
        return []
    cmds: List[str] = []
    for line in blocks[0].splitlines():
        line = line.strip()
        if not line or line.startswith("#"): continue
        if line.startswith("$ "): line = line[2:].strip()
        cmds.append(line)
    return cmds

def verify(repo: pathlib.Path, cfg: Dict[str, Any], task_md_text: str) -> Tuple[bool, str]:
    cmds = extract_verification_commands(task_md_text) if cfg.get("prefer_task_md_verification", True) else []
    if not cmds:
        cmds = list(cfg.get("default_verify_commands", ["python -m compileall -q ."]))
    out_lines = []
    ok = True
    for c in cmds:
        out_lines.append(f"$ {c}")
        rc, so, se = run_shell(c, repo)
        if so.strip(): out_lines.append(so.strip())
        if se.strip(): out_lines.append(se.strip())
        if rc != 0:
            ok = False
            out_lines.append(f"(FAILED rc={rc})")
            break
    return ok, "\n".join(out_lines)

def read_file(repo: pathlib.Path, rel: str, max_chars=20000) -> str:
    p = repo / rel
    if not p.exists(): return f"(missing: {rel})"
    return p.read_text(encoding="utf-8", errors="ignore")[:max_chars]

def load_config(repo: pathlib.Path) -> Dict[str, Any]:
    cfg = load_json(repo/".codex"/"config.json")
    if not cfg:
        cfg = load_json(repo/".codex"/"config.example.json") or {}
    cfg.setdefault("runner_version", RUNNER_VERSION)
    cfg.setdefault("codex_command", "codex")
    cfg.setdefault("codex_subcommand", "exec")
    cfg.setdefault("sandbox", "workspace-write")
    cfg.setdefault("use_full_auto_if_supported", True)
    cfg.setdefault("codex_skip_git_repo_check", "auto")  # auto|true|false
    cfg.setdefault("max_attempts_per_task", 25)
    cfg.setdefault("diff_ignore_paths", DEFAULT_IGNORE_PATHS)
    cfg.setdefault("default_verify_commands", ["python -m compileall -q ."])
    cfg.setdefault("prefer_task_md_verification", True)
    cfg.setdefault("require_codex_success", True)
    cfg.setdefault("require_task_must_change_globs", True)
    cfg.setdefault("require_task_md_updated", True)
    cfg.setdefault("require_nonce_in_task_md", True)
    return cfg

def eligible(task: Dict[str, Any], done_ids: set) -> bool:
    return all(d in done_ids for d in task.get("depends_on", []))

def pick_next(queue: List[Dict[str, Any]], state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    cur = state.get("current_task_id")
    if cur:
        for t in queue:
            if t["id"] == cur and t.get("status") != "done":
                return t
    done_ids = {t["id"] for t in queue if t.get("status") == "done"}
    candidates = [t for t in queue if t.get("status") in ("todo","doing") and eligible(t, done_ids)]
    if not candidates:
        return None
    candidates.sort(key=lambda t: (PRIORITY_ORDER.get(t.get("priority","P9"), 9), t["id"]))
    return candidates[0]

def git_diff_hash(repo: pathlib.Path, exclude_paths: List[str]) -> str:
    pathspecs = ["--", "."]
    for ign in exclude_paths:
        p = ign[:-1] if ign.endswith("/") else ign
        pathspecs.append(f":(exclude){p}")
    rc1, so1, se1 = run(["git", "diff", "--no-ext-diff"] + pathspecs, repo)
    rc2, so2, se2 = run(["git", "diff", "--no-ext-diff", "--cached"] + pathspecs, repo)
    blob = (so1 or "") + (so2 or "")
    return hashlib.sha256(blob.encode("utf-8", errors="ignore")).hexdigest()

def codex_caps(repo: pathlib.Path, codex: str) -> Dict[str, bool]:
    rc, so, se = run([codex, "exec", "--help"], repo)
    txt = (so or "") + (se or "")
    def has(flag: str) -> bool:
        return flag in txt
    return {
        "has_full_auto": has("--full-auto"),
        "has_skip_git": has("--skip-git-repo-check"),
        "has_sandbox": has("--sandbox") or has("-s"),
    }

def call_codex(repo: pathlib.Path, prompt: str, cfg: Dict[str, Any], caps: Dict[str,bool], force_skip_git: bool) -> Tuple[int,str]:
    codex = cfg.get("codex_command","codex")
    cmd = [codex, "exec"]
    if caps.get("has_sandbox", True):
        cmd += ["--sandbox", cfg.get("sandbox","workspace-write")]
    if cfg.get("use_full_auto_if_supported", True) and caps.get("has_full_auto", False):
        cmd += ["--full-auto"]
    if force_skip_git and caps.get("has_skip_git", False):
        cmd += ["--skip-git-repo-check"]
    cmd += ["-"]  # stdin
    rc, so, se = run(cmd, repo, input_text=prompt)
    out = (so or "") + ("\n" + se if se else "")
    return rc, out

def build_prompt(repo: pathlib.Path, task: Dict[str, Any], nonce: str) -> str:
    agents = read_file(repo, "AGENTS.md", max_chars=16000)
    task_md = read_file(repo, task["path"], max_chars=18000)

    contracts_text = []
    for c in task.get("contracts", []):
        contracts_text.append(f"\n\n---\n## CONTRACT: {c}\n")
        contracts_text.append(read_file(repo, c, max_chars=12000))

    skill_text = []
    skill_root = repo / "agentskills" / "skills"
    if skill_root.exists():
        for sid in task.get("skills", []):
            candidates = list(skill_root.glob(f"{sid}*.md"))
            if candidates:
                rel = candidates[0].relative_to(repo)
                skill_text.append(f"\n\n---\n## SKILL: {sid} ({rel})\n")
                skill_text.append(read_file(repo, str(rel), max_chars=12000))

    must_globs = task.get("must_change_globs", [])
    return f"""You are implementing task #{task['id']} ({task.get('priority')}): {task.get('title')}

AUTOMATION NONCE (MUST be pasted into the task md Completion Evidence): {nonce}

ABSOLUTE RULES:
- Do not ask questions. Make reasonable assumptions and proceed.
- Do not stop for approvals.
- Do NOT switch tasks.
- Prefer compact code; avoid unnecessary boilerplate/abstractions.
- If your changes make code/files unused, delete them in this task.
- Follow docs contracts, especially ClearML UI hygiene.

NON-NEGOTIABLE COMPLETION:
- You MUST update the task md: {task['path']} and include the NONCE.
- You MUST change at least one file matching must_change_globs: {must_globs}
- Verification commands in the task md must pass.

=== AGENTS.md ===
{agents}

=== TASK SPEC ===
{task_md}

=== CONTRACTS ===
{''.join(contracts_text) if contracts_text else '(none)'}

=== SKILLS ===
{''.join(skill_text) if skill_text else '(none)'}

Output requirements:
- Summarize changes concisely.
- List files changed.
- State verification commands run and results.
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--task", type=int, default=None)
    args = ap.parse_args()

    repo = pathlib.Path(args.repo).resolve()
    cfg = load_config(repo)

    print(f"codex_loop runner {cfg.get('runner_version','unknown')}")

    if shutil.which(cfg.get("codex_command","codex")) is None:
        print("ERROR: codex command not found.", file=sys.stderr)
        return 3

    queue_path = repo / "work" / "queue.json"
    state_path = repo / "work" / "_runner_state.json"
    runs_dir = repo / "work" / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    queue = load_json(queue_path, default=[])
    if not queue:
        print("ERROR: work/queue.json missing or empty", file=sys.stderr)
        return 2

    caps = codex_caps(repo, cfg.get("codex_command","codex"))
    (runs_dir / "_codex_caps.json").write_text(json.dumps(caps, ensure_ascii=False, indent=2), encoding="utf-8")

    state = load_json(state_path, default={}) or {}
    if args.task is not None:
        state["current_task_id"] = args.task
        save_json(state_path, state)

    ignore_paths = list(cfg.get("diff_ignore_paths", DEFAULT_IGNORE_PATHS))

    while True:
        queue = load_json(queue_path, default=[])
        state = load_json(state_path, default={}) or {}

        t = pick_next(queue, state)
        if not t:
            print("No eligible tasks found. (All done or blocked by dependencies)")
            return 0

        must_globs = t.get("must_change_globs", [])
        if cfg.get("require_task_must_change_globs", True) and not must_globs:
            print(f"ERROR: task {t['id']} missing must_change_globs.", file=sys.stderr)
            return 4

        # status -> doing
        if t.get("status") == "todo":
            t["status"] = "doing"
            for i,x in enumerate(queue):
                if x["id"] == t["id"]:
                    queue[i] = t
            save_json(queue_path, queue)

        state["current_task_id"] = t["id"]
        save_json(state_path, state)

        task_run_root = runs_dir / f"task_{t['id']:03d}"
        task_run_root.mkdir(parents=True, exist_ok=True)

        max_attempts = int(cfg.get("max_attempts_per_task", 25))

        for attempt in range(1, max_attempts+1):
            attempt_dir = task_run_root / f"attempt_{attempt:02d}"
            if attempt_dir.exists():
                continue
            attempt_dir.mkdir(parents=True, exist_ok=True)

            nonce = uuid.uuid4().hex
            prompt = build_prompt(repo, t, nonce)
            (attempt_dir/"prompt.txt").write_text(prompt, encoding="utf-8")

            rc, por, _ = git_porcelain(repo)
            before_dirty = parse_dirty_files(por) if rc == 0 else []
            before_filtered = set(filter_ignored(before_dirty, ignore_paths))
            before_hash = git_diff_hash(repo, ignore_paths) if rc == 0 else ""

            task_md_path = t["path"]
            task_md_before = read_file(repo, task_md_path, max_chars=200000)

            skip_policy = cfg.get("codex_skip_git_repo_check","auto")
            force_skip = (skip_policy is True)

            rc_codex, out = call_codex(repo, prompt, cfg, caps, force_skip_git=force_skip)
            if skip_policy == "auto" and ("Not inside a trusted directory" in out or "skip-git-repo-check" in out):
                rc2, out2 = call_codex(repo, prompt, cfg, caps, force_skip_git=True)
                if rc2 == 0 or out2.strip():
                    rc_codex, out = rc2, out2

            (attempt_dir/"codex_returncode.txt").write_text(str(rc_codex), encoding="utf-8")
            (attempt_dir/"codex_output.txt").write_text(out, encoding="utf-8")
            (task_run_root/"last_codex_output.txt").write_text(out, encoding="utf-8")

            rcA, porA, _ = git_porcelain(repo)
            after_dirty = parse_dirty_files(porA) if rcA == 0 else []
            after_filtered = set(filter_ignored(after_dirty, ignore_paths))
            after_hash = git_diff_hash(repo, ignore_paths) if rcA == 0 else ""

            progress = (after_filtered != before_filtered) or (after_hash != before_hash)

            must_ok = any(match_any_glob(p, must_globs) for p in after_filtered)
            task_md_updated = (task_md_path in after_dirty)
            task_md_after = read_file(repo, task_md_path, max_chars=250000)
            nonce_ok = (nonce in task_md_after)

            ok_verify, vout = verify(repo, cfg, task_md_after)
            (attempt_dir/"verification.txt").write_text(vout, encoding="utf-8")

            if cfg.get("require_codex_success", True) and rc_codex != 0:
                (attempt_dir/"guard_failed.txt").write_text("codex_returncode_nonzero", encoding="utf-8")
                print(f"Task {t['id']} codex failed (rc={rc_codex}); retrying...")
                time.sleep(0.5); continue

            if not progress:
                (attempt_dir/"guard_failed.txt").write_text("no_progress", encoding="utf-8")
                print(f"Task {t['id']} no progress detected; retrying...")
                time.sleep(0.5); continue

            if cfg.get("require_task_must_change_globs", True) and not must_ok:
                (attempt_dir/"guard_failed.txt").write_text("must_change_globs_not_touched", encoding="utf-8")
                print(f"Task {t['id']} did not touch required paths {must_globs}; retrying...")
                time.sleep(0.5); continue

            if cfg.get("require_task_md_updated", True) and not task_md_updated:
                (attempt_dir/"guard_failed.txt").write_text("task_md_not_updated", encoding="utf-8")
                print(f"Task {t['id']} did not update task md; retrying...")
                time.sleep(0.5); continue

            if cfg.get("require_nonce_in_task_md", True) and not nonce_ok:
                (attempt_dir/"guard_failed.txt").write_text("nonce_missing_in_task_md", encoding="utf-8")
                print(f"Task {t['id']} missing NONCE in task md; retrying...")
                time.sleep(0.5); continue

            if not ok_verify:
                print(f"Task {t['id']} verification failed; retrying... (attempt {attempt}/{max_attempts})")
                time.sleep(0.5); continue

            for i,x in enumerate(queue):
                if x["id"] == t["id"]:
                    queue[i]["status"] = "done"
            save_json(queue_path, queue)
            state["current_task_id"] = None
            save_json(state_path, state)
            print(f"Task {t['id']} DONE")
            break

        else:
            print(f"Task {t['id']} exceeded max attempts ({max_attempts}).", file=sys.stderr)
            return 10

        if args.once:
            return 0

if __name__ == "__main__":
    raise SystemExit(main())
