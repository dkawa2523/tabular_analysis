#!/usr/bin/env python
import argparse, pathlib, sys

REQUIRED = [
    "docs/00_INVARIANTS.md",
    "work/queue.json",
    "agentskills/ROUTER.md",
    "tools/codex_loop/run.py",
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    args = ap.parse_args()
    repo = pathlib.Path(args.repo).resolve()
    platform_src = repo.parent / "ml-platform" / "src"
    if platform_src.exists():
        sys.path.insert(0, str(platform_src))

    missing = []
    for r in REQUIRED:
        if not (repo / r).exists():
            missing.append(r)

    if missing:
        print("DOCTOR FAILED: missing files:")
        for m in missing:
            print(" -", m)
        return 1

    src = repo / "src"
    if src.exists():
        sys.path.insert(0, str(src))
        # Import check: platform uses ml_platform, solution uses usecase
        try:
            import ml_platform  # noqa: F401
            print("Import OK: ml_platform")
        except Exception:
            try:
                import usecase  # noqa: F401
                print("Import OK: usecase")
            except Exception as e:
                print("Import FAILED:", e)
                return 2

    print("DOCTOR OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
