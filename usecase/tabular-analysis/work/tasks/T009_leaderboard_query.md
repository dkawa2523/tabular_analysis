# Task 009: leaderboard: ClearMLから学習タスクを集約するクエリ実装（task_id基準）

Status: todo  
Priority: P0

## Goal
leaderboard が **task_id 基準**で train タスクから必要情報を取得できるようにする。

## Scope
### In scope
- fetch_train_task_summary(task_id) を実装
- train タスクの契約（Properties/Artifacts/Scalars）に沿って取得
- optional: project/tags filter から task_id list を得る

### Out of scope
- 可視化やランキング（T010）

## Contracts (must follow)
- `docs/03_CLEARML_UI_CONTRACT.md`
- `docs/06_ARTIFACT_CONTRACT.md`

## Depends on
5, 7

## Steps
1. train タスクが保存する情報（model_id, preprocess_name, metrics）を決め、その取得ロジックを実装
2. ClearML API で scalars / artifacts / parameters のどれから取るかを統一
3. 取得失敗時のエラーメッセージを改善（どの契約が欠けているか）

## Acceptance Criteria
- [ ] task_id を渡すと {model_id, model_name, primary_metric, primary_score, preprocess_name, dataset_id,...} が返る
- [ ] 不足情報があれば説明的に落ちる

## Verification
- `python -c "from tabular_analysis.integrations.clearml.leaderboard_query import fetch_train_task_summary; print('TODO: run with real task_id')"`


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
- 仕様の核: leaderboardは train の親ではなく、後段の集約分析タスク。

## Next Improvements (Codex MUST write)
- (write suggestions for next tasks)

## RESULT
- NONCE: 
- RESULT: (TODO)  # Must be set to DONE to complete task
- Evidence (files/commands):
