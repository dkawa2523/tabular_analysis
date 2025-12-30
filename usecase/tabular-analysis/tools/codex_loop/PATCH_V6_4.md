# v6.4 patch: Fix priority parsing in tools/codex_loop/run.py

## What this fixes
Your queue.json uses priorities like `P0`, `P1` etc.
The current `run.py` tries to do `int("P0")` and crashes.

This patch updates the sorting to robustly parse priority/id strings.

## Apply
From `tabular-analysis/` root:

```bash
python tools/codex_loop/patch_apply_v6_4.py
```

Then retry:

```bash
python tools/codex_loop/run.py --repo . --once
```

## Rollback
If needed, restore from the created backup:

`tools/codex_loop/run.py.bak.<timestamp>`
