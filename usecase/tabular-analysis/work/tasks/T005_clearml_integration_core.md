# Task 005: ClearML統合の核（init/connect_hparams/properties/artifacts/plots/debug）

Status: todo  
Priority: P0

## Goal
ClearML連携を `integrations/clearml/` に集約し、各タスクからの呼び出しを単純化する。

## Scope
### In scope
- Task.init の共通化（auto_connect_arg_parser を無効化）
- HyperParameters の接続を明示的に行う（full config 接続禁止）
- User Properties/Artifacts/Plots/Debug Samples の helper を提供
- UI clone / template task 用の set_script を config で制御できる
- Task reuse を避ける仕組み（reuse_task=false）を用意

### Out of scope
- 各タスク固有の可視化内容（タスク側）

## Contracts (must follow)
- `docs/03_CLEARML_UI_CONTRACT.md`
- `AGENTS.md`

## Depends on
1

## Steps
1. `integrations/clearml/task.py` の TODO を実装
2. config の `run.clearml.code.*` により `task.set_script(...)` を設定できるように
3. trusted directory 問題に備え、README に `--skip-git-repo-check` の扱いを整理（selfcheckで対応）
4. ClearMLが無い/未設定でも落ちないよう、enabled=false なら no-op にする

## Acceptance Criteria
- [ ] enabled=false で import してもエラーにならない
- [ ] enabled=true で Task.init できる（最小）
- [ ] HyperParameters に full config が入らない

## Verification
- `python -c "from tabular_analysis.integrations.clearml.task import init_task_if_enabled; print(init_task_if_enabled({'enabled':False}, 'x','training','p',[]))"`


## Platform reuse checklist (Codex MUST fill)
- Reused from ml-platform:
  - 
- Missing in ml-platform / implemented in solution:
  - 
- TODO candidates to move to platform:
  - 

## Risks addressed (Codex MUST fill; map to docs/09_RISKS_AND_MITIGATIONS.md)
- A (traceability):
- B (leaderboard target selection):
- C (comparability/leak/skew):
- D (ClearML UI hygiene):
- E (local/agent/clone):
- F (grid explosion control):
- G (bloat/cleanup):

## Notes / Risks
- ClearML仕様を集約するのが目的。タスク側に ClearML 直書きを増やさない。

## Next Improvements (Codex MUST write)
- (write suggestions for next tasks)

## RESULT
- NONCE: 
- RESULT: (TODO)  # Must be set to DONE to complete task
- Evidence (files/commands):
