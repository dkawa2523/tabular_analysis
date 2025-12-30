#!/usr/bin/env python
"""Doctor checks for platform reuse readiness."""
from __future__ import annotations
import argparse, pathlib, sys

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--platform-path", default="../../../ml-platform")
    args = ap.parse_args()
    repo = pathlib.Path(__file__).resolve().parents[1]
    platform = (repo / args.platform_path).resolve()
    if not platform.exists():
        print("FAIL: ml-platform not found:", platform)
        return 2

    # try import in editable mode assumptions
    sys.path.insert(0, str((platform / "src").resolve()))
    try:
        import ml_platform  # type: ignore
        print("OK: import ml_platform")
    except Exception as e:
        print("WARN: cannot import ml_platform from platform/src:", e)
        print("Hint: ensure you installed ml-platform editable: pip install -e ../../../ml-platform")
        # not fatal: platform may use different package name
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
