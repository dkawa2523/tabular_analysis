"""Patch tool for codex_loop run.py (v6.4)

Fixes: queue.json 'priority' values like 'P0' causing ValueError in run.py sorting.

Usage:
  python tools/codex_loop/patch_apply_v6_4.py

This script:
  - Creates a backup: tools/codex_loop/run.py.bak.<timestamp>
  - Patches the first occurrence of a line containing 'eligible.sort(key=lambda x:' inside run.py
    to use robust parsing for priority/id.
"""

from __future__ import annotations

from pathlib import Path
import sys
import datetime


def _patch_run_py(run_py: Path) -> None:
    if not run_py.exists():
        raise FileNotFoundError(f"run.py not found: {run_py}")

    text = run_py.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    target_idx = None
    for i, line in enumerate(lines):
        if "eligible.sort(key=lambda x:" in line:
            target_idx = i
            break

    if target_idx is None:
        raise RuntimeError("Could not find target line containing 'eligible.sort(key=lambda x:' in run.py")

    orig_line = lines[target_idx]
    indent = orig_line[: len(orig_line) - len(orig_line.lstrip(" \t"))]

    snippet = [
        f"{indent}def _to_int(v, default=999):\n",
        f"{indent}    \"\"\"Best-effort int conversion for priority/id (supports 'P0', '001', 'T12', etc.)\"\"\"\n",
        f"{indent}    if v is None:\n",
        f"{indent}        return default\n",
        f"{indent}    if isinstance(v, bool):\n",
        f"{indent}        # bool is subclass of int; treat explicitly\n",
        f"{indent}        return int(v)\n",
        f"{indent}    if isinstance(v, int):\n",
        f"{indent}        return v\n",
        f"{indent}    if isinstance(v, str):\n",
        f"{indent}        s = v.strip()\n",
        f"{indent}        digits = \"\".join(ch for ch in s if ch.isdigit())\n",
        f"{indent}        if digits:\n",
        f"{indent}            try:\n",
        f"{indent}                return int(digits)\n",
        f"{indent}            except Exception:\n",
        f"{indent}                return default\n",
        f"{indent}        # common forms\n",
        f"{indent}        up = s.upper()\n",
        f"{indent}        if up.startswith('P') and up[1:].isdigit():\n",
        f"{indent}            try:\n",
        f"{indent}                return int(up[1:])\n",
        f"{indent}            except Exception:\n",
        f"{indent}                return default\n",
        f"{indent}    return default\n",
        f"\n",
        f"{indent}eligible.sort(key=lambda x: (_to_int(x.get('priority', 999), 999), _to_int(x.get('id', 999), 999)))\n",
    ]

    # Replace the single line with snippet
    lines[target_idx : target_idx + 1] = snippet

    patched = "".join(lines)

    # Backup
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = run_py.with_name(run_py.name + f".bak.{ts}")
    backup.write_text(text, encoding="utf-8")

    run_py.write_text(patched, encoding="utf-8")

    print("OK: patched", run_py)
    print("Backup:", backup)


def main() -> int:
    here = Path(__file__).resolve()
    run_py = here.parent / "run.py"
    try:
        _patch_run_py(run_py)
    except Exception as e:
        print("ERROR:", e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
