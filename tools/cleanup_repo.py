#!/usr/bin/env python
"""Repository cleanup utility (conservative)."""
import argparse, pathlib, shutil

DEFAULT_PATTERNS = [
    "outputs",
    "multirun",
    ".clearml_cache",
    "**/__pycache__",
    "*.pyc",
    ".codex_exec_selfcheck.txt",
    "work/runs",
    "work/_runner_state.json",
]

def iter_matches(repo: pathlib.Path, pattern: str):
    if "**" in pattern or pattern.startswith("**/"):
        return repo.rglob(pattern.replace("**/", ""))
    return repo.glob(pattern)

def _skip_path(path: pathlib.Path) -> bool:
    parts = path.parts
    return ".git" in parts or ".venv" in parts

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--dry-run", action="store_true", default=False)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    repo = pathlib.Path(args.repo).resolve()
    dry = args.dry_run or not args.apply

    targets = set()
    for pat in DEFAULT_PATTERNS:
        for p in iter_matches(repo, pat):
            if _skip_path(p):
                continue
            targets.add(p)

    if not targets:
        print("No cleanup targets found.")
        return 0

    print("Cleanup targets:")
    for p in sorted(targets):
        print(" -", p.relative_to(repo))

    if dry:
        print("\nDry-run only. Use --apply to delete.")
        return 0

    for p in sorted(targets, reverse=True):
        try:
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
            else:
                p.unlink(missing_ok=True)
        except Exception as e:
            print("Failed:", p, e)

    print("Done.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
