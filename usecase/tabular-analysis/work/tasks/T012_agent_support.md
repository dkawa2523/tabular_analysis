# Task 012: ClearML Agent / template clone 実行の下準備（set_script/queue/clone契約）

Status: todo  
Priority: P1

## Goal
後から ClearML Agent 実行へ移行できるよう、code tracking と clone 実行の契約を整える。

## Scope
### In scope
- run.clearml.code.set_script=true で task.set_script(...) を設定できる
- queue 指定で execute_remotely できる（タスク単体）
- pipeline で template clone 実行する場合の設計メモを docs に反映

### Out of scope
- 実際の Agent 環境でのE2E検証（ユーザー環境依存）

## Contracts (must follow)
- `docs/07_AGENT_EXECUTION.md`

## Depends on
11

## Steps
1. `integrations/clearml/task.py` に set_script と queue の制御を実装
2. README に template task の作り方を追記

## Acceptance Criteria
- [ ] ローカル実行でも set_script を設定できる（ClearML UIで repoが追跡される）
- [ ] queue を設定して execute_remotely できる（手元ではdry-runでOK）

## Verification
- `python -c "print('TODO: verify in real ClearML Agent env')"`


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
- Agent は後回し。まず local を壊さない設計を優先。

## Next Improvements (Codex MUST write)
- (write suggestions for next tasks)

## RESULT
- NONCE: 
- RESULT: (TODO)  # Must be set to DONE to complete task
- Evidence (files/commands):
