# codex_loop (v6.2 patch)

This folder contains a minimal, robust runner to execute Codex-driven tasks.

## Key compatibility fixes
- `codex exec` prompt is passed as a **positional argument** (not stdin).
- Valid sandbox modes:
  - `read-only`
  - `workspace-write` (recommended)
  - `danger-full-access`

## First step
Run the selfcheck:

```bash
bash tools/codex_loop/selfcheck_codex_exec.sh
```

It will:
- detect whether `--skip-git-repo-check` is supported
- try sandbox modes (workspace-write → danger-full-access → read-only)
- write `tools/codex_loop/runtime.json`

## Run one task
```bash
python tools/codex_loop/run.py --repo . --once
```

## Logs
Each run writes logs under:
- `work/runs/task_XXX/`
