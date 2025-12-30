# Task 010: leaderboard タスク（比較・可視化・推奨model_id）

Status: todo  
Priority: P0

## Goal
train タスク群を集約し、ユーザーが最良モデルを選べる形で可視化/要約する。

## Scope
### In scope
- 入力: task_ids（基本）＋ optional filters
- 出力: leaderboard.csv, selection_rationale.md, recommended_model_id
- Plots: 上位Nの比較（順序を固定）
- User Properties: recommended_model_id/name/score
- HyperParameters: leaderboard.* のみ（他は入れない）

### Out of scope
- SHAPなど重たい可視化（train側）

## Contracts (must follow)
- `docs/03_CLEARML_UI_CONTRACT.md`
- `docs/06_ARTIFACT_CONTRACT.md`

## Depends on
9

## Steps
1. `flows/leaderboard.py` を実装し、query結果をDataFrame化してランキング
2. 可視化は最小（上位N棒グラフ、表）で、表示順序を安定化（番号prefix）
3. 推奨モデルの選定理由を `selection_rationale.md` に書く

## Acceptance Criteria
- [ ] leaderboard.csv が生成される
- [ ] recommended_model_id がPropertiesに設定される（ClearML on時）
- [ ] Plots が見やすく順序が安定している

## Verification
- `python -m tabular_analysis.cli.leaderboard run.clearml.enabled=false leaderboard.task_ids=["TASK_ID_1","TASK_ID_2"]`


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
- 非DSはこのタスクだけ見れば良い（train詳細は必要時だけ）。

## Next Improvements (Codex MUST write)
- (write suggestions for next tasks)

## RESULT
- NONCE: 
- RESULT: (TODO)  # Must be set to DONE to complete task
- Evidence (files/commands):
