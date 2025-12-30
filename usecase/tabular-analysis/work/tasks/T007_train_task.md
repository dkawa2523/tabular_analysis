# Task 007: train タスク（独立タスク、ClearML UI出力、Model registry）

Status: todo  
Priority: P0

## Goal
train を独立タスクとして完成させ、ClearML上で比較に必要な情報を過不足なく残す。

## Scope
### In scope
- 入力: dataset_id(or local_path) + model config + train config
- 出力: metrics.json/cv_results.csv/model artifact (local) + model_id (clearml)
- Plots: pred-vs-true, residuals, (可能なら) importance
- Debug samples: 予測例（数件）
- User Properties: model_id/model_name/primary_metric/primary_score/dataset_id など
- 重要: 親子タスクは禁止（leaderboard が集約する）

### Out of scope
- leaderboard 実装（別タスク）

## Contracts (must follow)
- `docs/03_CLEARML_UI_CONTRACT.md`
- `docs/06_ARTIFACT_CONTRACT.md`
- `AGENTS.md`

## Depends on
4, 5, 6

## Steps
1. `flows/train.py` を実装し、preprocess bundle がある場合は適切に利用する（Skew/二重前処理防止）
2. ClearML enabled: `integrations/clearml/task.py` を用いて UI契約に沿ってログする
3. ClearML Model registry へ登録し model_id を Properties に残す
4. Artifacts を契約通り出す

## Acceptance Criteria
- [ ] run.clearml.enabled=false で学習が完了し outputs/train に成果物が出る
- [ ] run.clearml.enabled=true で task が作成され、Properties/Artifacts/Plots が確認できる
- [ ] HyperParameters に無関係項目が混入しない
- [ ] 親子タスクリンクを作っていない

## Verification
- `python -m tabular_analysis.cli.train run.clearml.enabled=false data.local_path=outputs/preprocess/data_processed.parquet data.target_col=target model.name=ridge`


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
- model_id の保存場所（Properties vs artifact）は leaderboard 側の取得容易性を優先して決める。

## Next Improvements (Codex MUST write)
- (write suggestions for next tasks)

## RESULT
- NONCE: 
- RESULT: (TODO)  # Must be set to DONE to complete task
- Evidence (files/commands):
