#!/usr/bin/env python3
"""Reconcile work/queue.json with work/tasks/*.md markers.

- If task markdown contains '- RESULT: DONE' or 'Status: done', set status=done.
- If status is 'doing', revert to todo unless markdown indicates DONE.

Usage:
  python tools/codex_loop/reconcile_queue.py --repo .
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def _save(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def _find_task_md(repo: Path, task: Dict[str, Any]) -> Optional[Path]:
    p = task.get("path")
    if isinstance(p, str) and p.strip():
        cand = (repo / p).resolve()
        if cand.exists():
            return cand
    tasks_dir = repo / "work" / "tasks"
    if not tasks_dir.exists():
        return None
    try:
        tid = int(str(task.get("id")))
    except Exception:
        return None
    pats = [f"T{tid:03d}_*.md", f"T{tid:03d}*.md"]
    for pat in pats:
        c = sorted(tasks_dir.glob(pat))
        if c:
            return c[0]
    return None

def _md_done(md: Path) -> bool:
    txt = md.read_text(encoding="utf-8", errors="ignore")
    if re.search(r"^Status:\s*done\b", txt, flags=re.I | re.M):
        return True
    if re.search(r"^-\s*RESULT:\s*DONE\b", txt, flags=re.I | re.M):
        return True
    return False

def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()
    qpath = repo / "work" / "queue.json"
    if not qpath.exists():
        print(f"ERROR: {qpath} not found")
        return 2
    queue = _load(qpath)
    if isinstance(queue, dict) and "tasks" in queue:
        tasks = queue["tasks"]
    elif isinstance(queue, list):
        tasks = queue
    else:
        print("ERROR: queue.json must be array or {tasks:[...]}")
        return 2

    changed = False
    for t in tasks:
        st = str(t.get("status","")).strip().lower()
        md = _find_task_md(repo, t)
        md_is_done = bool(md and _md_done(md))
        if md_is_done and st != "done":
            t["status"] = "done"
            changed = True
        elif st == "doing" and not md_is_done:
            t["status"] = "todo"
            changed = True

    if changed:
        _save(qpath, queue)
        print("OK: reconciled queue.json")
    else:
        print("OK: no changes")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
