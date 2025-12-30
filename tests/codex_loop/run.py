#!/usr/bin/env python3
"""
codex_loop runner for tabular-analysis

Design goals:
- Works with modern codex-cli: `codex exec --sandbox <MODE> <PROMPT>`
- Does NOT rely on git to detect progress (uses file snapshots)
- Avoids "auto-DONE": requires the task md to contain `RESULT: DONE`
- Leaves detailed logs under work/runs/task_XXX/
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


ALLOWED_SANDBOX = {"read-only", "workspace-write", "danger-full-access"}


def _now_iso() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def _read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _write_text(p: Path, s: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")


def _load_json(p: Path, default: Any) -> Any:
    if not p.exists():
        return default
    return json.loads(_read_text(p))


def _save_json(p: Path, obj: Any) -> None:
    _write_text(p, json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def _which(cmd: str) -> Optional[str]:
    from shutil import which
    return which(cmd)


def _cmd_ok(cmd: List[str], cwd: Path) -> bool:
    try:
        subprocess.run(cmd, cwd=cwd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def _codex_help() -> str:
    try:
        out = subprocess.check_output(["codex", "exec", "--help"], stderr=subprocess.STDOUT, text=True)
        return out
    except Exception as e:
        return str(e)


@dataclasses.dataclass
class CodexRuntime:
    sandbox_mode: str = "workspace-write"
    use_skip_git_repo_check: bool = False
    skip_git_repo_check_flag: Optional[str] = None

    @staticmethod
    def load(repo_root: Path) -> "CodexRuntime":
        runtime_file = repo_root / "tools" / "codex_loop" / "runtime.json"
        data = _load_json(runtime_file, {})
        # env override
        env_mode = os.environ.get("CODEX_SANDBOX_MODE", "").strip()
        mode = (env_mode or data.get("sandbox_mode") or "workspace-write").strip()

        if mode not in ALLOWED_SANDBOX:
            # fallback to safe default
            mode = "workspace-write"

        skip_flag = data.get("use_skip_git_repo_check", False)
        skip_name = data.get("skip_git_repo_check_flag")

        # If codex doesn't support the flag, disable
        help_out = _codex_help()
        supported = ("--skip-git-repo-check" in help_out)
        if not supported:
            skip_flag = False
            skip_name = None
        else:
            # If supported and user previously hit trusted-dir issue, enable by default
            skip_flag = bool(skip_flag) or True
            skip_name = "--skip-git-repo-check"

        return CodexRuntime(
            sandbox_mode=mode,
            use_skip_git_repo_check=bool(skip_flag),
            skip_git_repo_check_flag=skip_name,
        )

    def codex_cmd(self, prompt: str) -> List[str]:
        cmd = ["codex", "exec", "--sandbox", self.sandbox_mode]
        if self.use_skip_git_repo_check and self.skip_git_repo_check_flag:
            cmd.append(self.skip_git_repo_check_flag)
        cmd.append(prompt)
        return cmd


@dataclasses.dataclass
class TaskItem:
    id: int
    title: str
    path: str
    priority: int = 999
    status: str = "todo"
    depends_on: List[int] = dataclasses.field(default_factory=list)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "TaskItem":
        return TaskItem(
            id=int(d["id"]),
            title=str(d.get("title", "")),
            path=str(d.get("path", "")),
            priority=int(d.get("priority", 999)),
            status=str(d.get("status", "todo")),
            depends_on=list(map(int, d.get("depends_on", []) or [])),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "priority": self.priority,
            "status": self.status,
            "title": self.title,
            "path": self.path,
            "depends_on": self.depends_on or [],
        }


def load_queue(repo_root: Path) -> Tuple[Path, List[TaskItem]]:
    qpath = repo_root / "work" / "queue.json"
    raw = _load_json(qpath, None)
    if raw is None:
        raise FileNotFoundError(f"Missing {qpath}")
    if isinstance(raw, dict) and "tasks" in raw:
        tasks = [TaskItem.from_dict(x) for x in raw["tasks"]]
    elif isinstance(raw, list):
        tasks = [TaskItem.from_dict(x) for x in raw]
    else:
        raise ValueError("queue.json must be a list or {tasks:[...]}")
    return qpath, tasks


def save_queue(qpath: Path, tasks: List[TaskItem]) -> None:
    # preserve original shape: write list (simple)
    _save_json(qpath, [t.to_dict() for t in tasks])


def eligible(tasks: List[TaskItem]) -> List[TaskItem]:
    done = {t.id for t in tasks if t.status == "done"}
    out: List[TaskItem] = []
    for t in tasks:
        if t.status != "todo":
            continue
        if any(dep not in done for dep in t.depends_on):
            continue
        out.append(t)
    out.sort(key=lambda x: (x.priority, x.id))
    return out


def snapshot(repo_root: Path) -> Dict[str, str]:
    """
    Snapshot file content hashes for progress detection.
    Scope is intentionally limited to meaningful sources to avoid noise.
    """
    include_roots = [
        repo_root / "src",
        repo_root / "conf",
        repo_root / "docs",
        repo_root / "README.md",
        repo_root / "AGENTS.md",
        repo_root / "work" / "tasks",
    ]
    exclude_parts = {".venv", "__pycache__", ".git", "work/runs", "work/state.json"}
    snap: Dict[str, str] = {}

    def should_exclude(p: Path) -> bool:
        ps = str(p).replace("\\", "/")
        for ex in exclude_parts:
            if ex in ps:
                return True
        return False

    def file_hash(p: Path) -> str:
        h = hashlib.sha1()
        with p.open("rb") as f:
            while True:
                b = f.read(1024 * 1024)
                if not b:
                    break
                h.update(b)
        return h.hexdigest()

    for root in include_roots:
        if isinstance(root, Path) and root.is_file():
            if should_exclude(root):
                continue
            rel = str(root.relative_to(repo_root)).replace("\\", "/")
            snap[rel] = file_hash(root)
            continue
        if not (isinstance(root, Path) and root.exists()):
            continue
        if root.is_dir():
            for p in root.rglob("*"):
                if not p.is_file():
                    continue
                if should_exclude(p):
                    continue
                rel = str(p.relative_to(repo_root)).replace("\\", "/")
                # Avoid hashing huge binary data by extension (optional)
                snap[rel] = file_hash(p)
    return snap


def diff_snap(a: Dict[str, str], b: Dict[str, str]) -> List[str]:
    paths = sorted(set(a.keys()) | set(b.keys()))
    changed = [p for p in paths if a.get(p) != b.get(p)]
    return changed


def parse_verification_commands(task_md: str) -> List[str]:
    """
    Extract verification commands from a TASK.md.
    Supported forms:
    - fenced code blocks under a heading containing 'Verification'
    - list items containing `command` in backticks
    """
    cmds: List[str] = []
    # fenced blocks
    fence_re = re.compile(r"```(?:bash|sh)?\n(.*?)\n```", re.S)
    for m in fence_re.finditer(task_md):
        block = m.group(1).strip()
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            cmds.append(line)

    # inline backticks (list items)
    for line in task_md.splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        inlines = re.findall(r"`([^`]+)`", line)
        for cmd in inlines:
            cmd = cmd.strip()
            if cmd:
                cmds.append(cmd)

    # de-dup preserve order
    seen = set()
    out = []
    for c in cmds:
        if c in seen:
            continue
        seen.add(c)
        out.append(c)
    return out


def run_shell(cmd: str, cwd: Path) -> Tuple[int, str]:
    p = subprocess.Popen(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out, _ = p.communicate()
    return p.returncode, out


def ensure_logs(task_run_dir: Path) -> None:
    task_run_dir.mkdir(parents=True, exist_ok=True)


def short_prompt_for_file(path: str) -> str:
    return (
        "Follow the instructions in the file:\n"
        f"{path}\n\n"
        "You MUST apply changes to the repository files (not just suggestions). "
        "Update the referenced TASK.md with `RESULT: DONE` only after verification passes."
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".", help="Repository root (tabular-analysis)")
    ap.add_argument("--once", action="store_true", help="Run only one eligible task")
    ap.add_argument("--task", type=int, default=None, help="Run a specific task id")
    args = ap.parse_args()

    repo_root = Path(args.repo).resolve()
    qpath, tasks = load_queue(repo_root)
    runtime = CodexRuntime.load(repo_root)

    run_root = repo_root / "work" / "runs"
    run_root.mkdir(parents=True, exist_ok=True)

    # pick task
    if args.task is not None:
        candidates = [t for t in tasks if t.id == args.task]
        if not candidates:
            print(f"No such task id: {args.task}")
            return 2
        t = candidates[0]
        deps_done = all(next((x for x in tasks if x.id == dep and x.status == "done"), None) is not None for dep in t.depends_on)
        if t.status != "todo" or not deps_done:
            print(f"Task {t.id} is not eligible (status={t.status}, depends_on={t.depends_on})")
            return 3
        chosen = t
    else:
        elig = eligible(tasks)
        if not elig:
            print("No eligible tasks found. (All done or blocked by dependencies)")
            return 0
        chosen = elig[0]

    task_id = chosen.id
    task_md_path = (repo_root / chosen.path).resolve()
    if not task_md_path.exists():
        print(f"Task {task_id} refers to missing file: {task_md_path}")
        return 4

    run_dir = run_root / f"task_{task_id:03d}"
    ensure_logs(run_dir)

    # write prompt file (full)
    agents_md = (repo_root / "AGENTS.md")
    header = ""
    if agents_md.exists():
        header = _read_text(agents_md).strip() + "\n\n"

    task_body = _read_text(task_md_path)
    prompt_full = (
        header
        + "=== TASK FILE (source of truth) ===\n"
        + f"{task_md_path.relative_to(repo_root)}\n\n"
        + task_body
        + "\n\n=== REQUIRED OUTPUTS ===\n"
        + "- Make code changes in the repository.\n"
        + "- Update the TASK.md with implementation notes.\n"
        + "- Add `RESULT: DONE` ONLY if all verification commands pass.\n"
        + "- If you cannot finish, write `RESULT: BLOCKED` and explain.\n"
    )

    prompt_path = run_dir / "prompt.txt"
    _write_text(prompt_path, prompt_full)

    # snapshots for progress
    before = snapshot(repo_root)

    # codex exec
    codex_prompt = short_prompt_for_file(str(prompt_path.relative_to(repo_root)).replace("\\", "/"))
    cmd = runtime.codex_cmd(codex_prompt)

    codex_out = run_dir / "codex_output.txt"
    rc_file = run_dir / "codex_rc.txt"
    _write_text(run_dir / "cmd.txt", " ".join(shlex.quote(x) for x in cmd) + "\n")

    try:
        proc = subprocess.run(cmd, cwd=repo_root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        _write_text(codex_out, proc.stdout or "")
        _write_text(rc_file, str(proc.returncode))
    except Exception as e:
        _write_text(codex_out, f"Runner exception: {e}\n")
        _write_text(rc_file, "999")
        print(f"Task {task_id} FAILED: runner exception")
        print(f"  Logs: {run_dir}")
        return 5

    if proc.returncode != 0:
        tail = "\n".join((_read_text(codex_out)).splitlines()[-60:])
        print(f"Task {task_id} FAILED: codex exec returned rc={proc.returncode}")
        print(f"  Logs: {run_dir}")
        print("---- last codex output ----")
        print(tail)
        return 6

    # detect progress
    after = snapshot(repo_root)
    changed = diff_snap(before, after)
    _write_text(run_dir / "changed_paths.txt", "\n".join(changed) + ("\n" if changed else ""))

    if not changed:
        # fail fast: no progress detected
        print(f"Task {task_id} FAILED: no progress detected")
        print(f"  Logs: {run_dir}")
        print(f"   - prompt: {prompt_path}")
        print(f"   - codex:  {codex_out}")
        print(f"   - rc:     {rc_file}")
        print(f"   - changed:{run_dir / 'changed_paths.txt'}")
        return 7

    # run verification commands
    task_md_text_after = _read_text(task_md_path)
    verify_cmds = parse_verification_commands(task_md_text_after)
    verify_log = run_dir / "verification.txt"

    if verify_cmds:
        all_ok = True
        out_lines: List[str] = []
        for c in verify_cmds:
            out_lines.append(f"$ {c}")
            rc, out = run_shell(c, cwd=repo_root)
            out_lines.append(out.rstrip())
            out_lines.append(f"[rc={rc}]")
            if rc != 0:
                all_ok = False
        _write_text(verify_log, "\n".join(out_lines) + "\n")
        if not all_ok:
            print(f"Task {task_id} FAILED: verification failed")
            print(f"  Logs: {run_dir}")
            return 8
    else:
        _write_text(verify_log, "No verification commands found in TASK.md\n")

    # require RESULT: DONE marker
    if "RESULT: DONE" not in task_md_text_after:
        print(f"Task {task_id} FAILED: TASK.md missing `RESULT: DONE`")
        print(f"  Hint: codex must update {task_md_path.relative_to(repo_root)}")
        print(f"  Logs: {run_dir}")
        return 9

    # mark done
    for t in tasks:
        if t.id == task_id:
            t.status = "done"
            break
    save_queue(qpath, tasks)

    # update state
    state_path = repo_root / "work" / "state.json"
    state = _load_json(state_path, {})
    state.update(
        {
            "last_task_id": task_id,
            "last_status": "done",
            "last_run_dir": str(run_dir),
            "updated_at": _now_iso(),
        }
    )
    _save_json(state_path, state)

    print(f"Task {task_id} DONE")
    if not args.once:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
