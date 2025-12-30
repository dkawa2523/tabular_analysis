# Task 004: preprocess タスク（bundle + summary + preprocessed dataset）

Status: todo  
Priority: P0

## Goal
前処理を **独立タスク**として実行し、前処理済みDatasetと再現用bundle/recipe/summaryを必ず残す。

## Scope
### In scope
- 入力は dataset_id または local_path
- 前処理 bundle を `preprocess_bundle.joblib` として保存
- summary をカテゴリ別に分割して `preprocess_summary.md` に保存（入力/目的変数/欠損/スケール/エンコード等）
- clearml enabled: 前処理済みDatasetを新規作成し、preprocessed_dataset_id を記録
- Debug samples: 変換前後の少量比較（列数制限・先頭数行）

### Out of scope
- feature engineering の高度な処理（将来）
- SHAP等 heavy plot（train側）

## Contracts (must follow)
- `docs/03_CLEARML_UI_CONTRACT.md`
- `docs/06_ARTIFACT_CONTRACT.md`

## Depends on
2, 3

## Steps
1. `core/preprocessing.fit_transform_tabular` を sklearn ColumnTransformer で実装
2. 前処理対象列（numeric/categorical）を自動推定しつつ、将来の指定もできるように
3. `flows/preprocess.py` を実装し、outputs に parquet + bundle + recipe + summary を出す
4. ClearML enabled: dataset upload と UI出力（hparams/properties/artifacts/plots/debug）

## Acceptance Criteria
- [ ] run.clearml.enabled=false でも outputs/preprocess に成果物が出る
- [ ] preprocess_summary.md がカテゴリ別に読みやすい（1行に圧縮しない）
- [ ] clearml enabled で preprocessed_dataset_id が生成され、Properties に記録される

## Verification
- `python -m tabular_analysis.cli.preprocess run.clearml.enabled=false data.local_path=data/example.csv data.target_col=target`


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
- 前処理の『何をしたか』が後で確認できることが最重要（summary/recipe/manifest）。

## Next Improvements (Codex MUST write)
- (write suggestions for next tasks)

## RESULT
- NONCE: 
- RESULT: (TODO)  # Must be set to DONE to complete task
- Evidence (files/commands):
