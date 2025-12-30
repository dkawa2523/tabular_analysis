# codex_loop (tabular-analysis)

## What this tool does
- Reads `work/queue.json`
- Picks an eligible task (status=todo and deps done)
- Runs Codex CLI (`codex exec --sandbox <mode> "<PROMPT>"`)
- Detects real file changes via snapshot diff (works without git)
- Runs **verification commands** extracted from the task markdown
- Marks task done in queue only when:
  - verification passes (return code == 0 for all commands; stdout is allowed)
  - task md contains `- RESULT: DONE` and a NONCE
  - must_change_globs satisfied

## Logs
- `work/runs/task_XXX/`
  - `prompt.txt`
  - `codex_output.txt`
  - `codex_rc.txt`
  - `changed_paths.txt`
  - `verification.txt`
  - `verification_failed_cmd.txt` (only on failure)

## Selfcheck
Run:
```bash
bash tools/codex_loop/selfcheck_codex_exec.sh
```

It creates:
- `tools/codex_loop/codex_exec_selfcheck.log`
- `tools/codex_loop/runtime.json`
