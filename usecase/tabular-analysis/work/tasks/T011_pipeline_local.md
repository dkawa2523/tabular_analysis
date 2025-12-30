# Task 011: pipeline (local-first): preprocess×model を複数実行して leaderboard に task_id を渡す

Status: todo  
Priority: P0

## Goal
pipeline を “接着” として実装し、ユーザーが dataset_id を入力して一括評価できるようにする。

## Scope
### In scope
- pipeline.preprocess_grid と pipeline.models をループして preprocess/train を複数実行
- ClearML enabled の場合、各実行が独立 Task として作成され task_id を収集
- leaderboard を最後に実行し task_id list を渡す（ユーザー指定不要）

### Out of scope
- ClearML PipelineController の本格対応（T012）

## Contracts (must follow)
- `docs/07_PIPELINE_CONTRACT.md`
- `AGENTS.md`

## Depends on
3, 4, 7, 10

## Steps
1. `pipelines/local_pipeline.run_pipeline_local` を実装
2. cfg から各タスク用の部分設定を抽出して flows を呼ぶ（full config connect禁止）
3. task_id の受け渡しを統一（local時は疑似IDでも良いが、ClearML on時は実task_id）

## Acceptance Criteria
- [ ] pipeline が最後に leaderboard を実行できる
- [ ] ユーザーは task_id を手で入れなくて良い（pipelineが自動で渡す）
- [ ] 親子タスクを作らない

## Verification
- `python -m tabular_analysis.cli.pipeline run.clearml.enabled=false data.local_path=data/example.csv data.target_col=target`


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
- pipelineはあくまで接着。タスク実装を肥大化させない。

## Next Improvements (Codex MUST write)
- (write suggestions for next tasks)

## RESULT
- NONCE: 
- RESULT: (TODO)  # Must be set to DONE to complete task
- Evidence (files/commands):
