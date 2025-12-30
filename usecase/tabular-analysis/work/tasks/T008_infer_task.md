# Task 008: infer タスク（single/batch/optimize、逆変換、成果物/plots）

Status: todo  
Priority: P0

## Goal
推論タスクを独立実行可能にし、用途別成果物を ClearML に残す。

## Scope
### In scope
- model_id（ClearML）または local model path からロード
- preprocess bundle があれば適用し、目的変数変換があれば逆変換
- mode: single/batch/optimize を実装
- Artifacts 契約（predictions.csv 等）
- optimize は最初は random search で良い（後で optuna拡張）

### Out of scope
- 高度な制約最適化（将来）

## Contracts (must follow)
- `docs/03_CLEARML_UI_CONTRACT.md`
- `docs/06_ARTIFACT_CONTRACT.md`

## Depends on
5, 7

## Steps
1. `core/inference` を必要最小で実装（single/batch/optimize）
2. `flows/infer.py` を実装し、mode別に成果物を出す
3. ClearML enabled: Debug samples と最小 plots（optimize履歴）を出す

## Acceptance Criteria
- [ ] single: input json -> output json が生成される
- [ ] batch: predictions.csv が生成される
- [ ] optimize: trials.csv と best_solution.json が生成される

## Verification
- `python -m tabular_analysis.cli.infer run.clearml.enabled=false infer.mode=batch model.local_path=outputs/train/model.joblib infer.batch_input_path=data/infer_batch.csv`


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
- 目的: 非DSが推論結果を artifact で取り出せること。

## Next Improvements (Codex MUST write)
- (write suggestions for next tasks)

## RESULT
- NONCE: 
- RESULT: (TODO)  # Must be set to DONE to complete task
- Evidence (files/commands):
