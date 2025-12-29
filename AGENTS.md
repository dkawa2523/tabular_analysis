# AGENTS.md — Project Operating Rules (Codex must obey)

## Non-negotiables
- **One-task-at-a-time**. Do not work on multiple tasks in one attempt.
- **No questions**. Make assumptions and proceed.
- **Do not stop for approval**.
- **Keep code compact**. Prefer fewer files and simpler abstractions.
- **Review-friendly**. Keep changes localized; update `docs/15_CODEMAP.md` when entry points change.

## Polyrepo policy
- Platform repo: `ml-platform` is the contract + shared library.
- Solution repo: `ml-solution-<usecase>` owns only usecase-specific logic and config.
- Do not duplicate platform logic inside solution. Extend via registry/hooks.

## ClearML policy (UI hygiene)
- HyperParameters: only task-relevant knobs.
- Full config stored as Artifact (`config_full.yaml`).
- Parent training task plots must be minimal (leaderboard-centric).
- Model-specific heavy plots (scatter, SHAP) belong to child tasks only.

## Local & ClearML execution
- Every task must run locally with `run.clearml.enabled=false`.
- When `run.clearml.enabled=true`, tasks must:
  - init Task, log artifacts/plots/properties per contract
  - optionally support remote execution via agent:
    - `enqueue=true` -> `task.execute_remotely(queue_name=...)`
    - pipeline controller -> ClearML PipelineController
- For UI-launched runs, code must support `task.set_script(...)` using config (repository/branch/entrypoint).

## Deletion policy
- Every task: if changes make files/dirs unused, remove them in the same task.
- There is also a dedicated cleanup task later; still delete opportunistically when safe.

## Evidence rule (prevents false DONE)
- Each attempt has a **NONCE**. You must paste it into the task md completion section.
