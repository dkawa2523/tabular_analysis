#!/usr/bin/env python
"""Scan ../../../ml-platform for reusable utilities.

This is intentionally lightweight: it prints directory hints and greps for key tokens.
It writes output to work/runs/_platform_scan.txt.
"""
from __future__ import annotations

import os
import pathlib
import re
import sys
from datetime import datetime

TOKENS = [
    "clearml",
    "Task.init",
    "PipelineController",
    "set_script",
    "execute_remotely",
    "Dataset",
    "Model",
    "artifact",
    "connect",
    "hyperparam",
    "property",
    "registry",
]

def main() -> int:
    here = pathlib.Path(__file__).resolve()
    repo = here.parents[1]
    platform = (repo / "../../../ml-platform").resolve()
    out_dir = (repo / "work" / "runs")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "_platform_scan.txt"

    lines = []
    lines.append(f"platform_scan at {datetime.now().isoformat()}")
    lines.append(f"repo={repo}")
    lines.append(f"platform={platform}")
    if not platform.exists():
        lines.append("ERROR: ml-platform not found at expected relative path.")
        out_path.write_text("\n".join(lines), encoding="utf-8")
        print(out_path.read_text(encoding="utf-8"))
        return 2

    # tree summary (limited)
    lines.append("\n== platform tree (depth<=3) ==")
    for p in sorted(platform.rglob("*")):
        try:
            rel = p.relative_to(platform)
        except Exception:
            continue
        if len(rel.parts) > 3:
            continue
        if p.is_dir():
            continue
        if p.suffix not in (".py",".md",".txt",".toml",".yaml",".yml",".json"):
            continue
        lines.append(str(rel))

    # grep tokens
    lines.append("\n== token hits (light grep) ==")
    py_files = [p for p in platform.rglob("*.py") if p.is_file()]
    for tok in TOKENS:
        hits = []
        pat = re.compile(re.escape(tok))
        for f in py_files[:2000]:
            try:
                txt = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if pat.search(txt):
                hits.append(str(f.relative_to(platform)))
                if len(hits) >= 20:
                    break
        lines.append(f"- {tok}: {len(hits)} hits (show up to 20)")
        for h in hits:
            lines.append(f"  - {h}")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(out_path.read_text(encoding="utf-8"))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
