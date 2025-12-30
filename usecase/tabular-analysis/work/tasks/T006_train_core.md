# Task 006: train コア（CV + metrics + model save）

Status: todo  
Priority: P0

## Goal
学習ロジック（ClearML非依存）を core に実装し、独立タスクから再利用できるようにする。

## Scope
### In scope
- CV 分割（kfold）を実装
- metrics: primary + others を計算
- OOF予測（必要なら）を保存できる
- model は registry 経由で生成する

### Out of scope
- ClearML UI 出力（T007）

## Contracts (must follow)
- `docs/06_ARTIFACT_CONTRACT.md`
- `AGENTS.md`

## Depends on
2

## Steps
1. `core/training.train_model_cv` を実装
2. sklearn の Pipeline/ColumnTransformer との整合（Xが sparse/ndarray でも動く）を確認
3. random_state/seed の扱いを split_cfg に統一

## Acceptance Criteria
- [ ] Ridge で学習し、rmse/mae/r2 が返る
- [ ] 例外時に説明的なエラーを出す（データ形状/target欠落など）

## Verification
- `python -c "import numpy as np; from tabular_analysis.core.training import train_model_cv; X=np.random.randn(50,3); y=np.random.randn(50); r=train_model_cv(X,y,'ridge',{'alpha':1.0}, {'kind':'kfold','n_splits':3,'shuffle':True,'seed':0}, {'primary':'rmse','others':['mae','r2']}); print(r.metrics)"`


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
- core は ClearML に依存しない。必ず分離。

## Next Improvements (Codex MUST write)
- (write suggestions for next tasks)

## RESULT
- NONCE: 
- RESULT: (TODO)  # Must be set to DONE to complete task
- Evidence (files/commands):
