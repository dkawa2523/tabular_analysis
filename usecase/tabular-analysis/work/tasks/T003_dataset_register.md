# Task 003: dataset_register タスク（local first + ClearML Dataset optional）

Status: todo  
Priority: P0

## Goal
ローカルCSV/Parquetを検証し、ClearML enabled の場合は Dataset として登録できるようにする。

## Scope
### In scope
- local: schema.json/head.csv/manifest.json を outputs に出す
- clearml: Dataset を作成して dataset_id を Properties/Artifacts に記録
- HyperParameters は data.local_path/format など最小のみ
- Debug samples に head/tail を出す（過剰に出さない）

### Out of scope
- 前処理（T004）
- 学習/推論

## Contracts (must follow)
- `docs/03_CLEARML_UI_CONTRACT.md`
- `docs/06_ARTIFACT_CONTRACT.md`

## Depends on
1, 2

## Steps
1. `flows/dataset_register.py` を実装（run.clearml.enabled に応じて分岐）
2. core/data_io を使ってローカル読み込みを確実にする（encoding等は最小）
3. ClearML enabled の場合、Dataset を作成し `dataset_id` を返す/保存する
4. Artifacts: schema.json/head.csv/manifest.json/config_effective.yaml を出す

## Acceptance Criteria
- [ ] run.clearml.enabled=false でも成功し、outputs に artifacts が出る
- [ ] run.clearml.enabled=true で ClearML Dataset が作成され、dataset_id が記録される
- [ ] HyperParameters に関係ない項目が混入しない

## Verification
- `python -m tabular_analysis.cli.dataset_register run.clearml.enabled=false data.local_path=data/example.csv`
- `python -m tabular_analysis.cli.dataset_register run.clearml.enabled=true data.local_path=data/example.csv`


## Platform reuse checklist (Codex MUST fill)
- Reused from ml-platform:
  - ml_platform.integrations.clearml (task_factory/connect_hparams/set_user_properties/upload_artifact/apply_ui_hygiene)
  - ml_platform.config.export_config_artifact
- Missing in ml-platform / implemented in solution:
  - ClearML Dataset helper (create_dataset_from_files/get_local_copy_if_dataset_id)
- TODO candidates to move to platform:
  - ClearML Dataset helper in `src/tabular_analysis/integrations/clearml/dataset.py`

## Risks addressed (Codex MUST fill; map to docs/09_RISKS_AND_MITIGATIONS.md)
- A (traceability): manifest.json includes local_path+sha256; user properties include usecase_id/process
- B (leaderboard target selection):
- C (comparability/leak/skew):
- D (ClearML UI hygiene): HyperParameters limited to data.local_path/format; artifacts in outputs
- E (local/agent/clone): local paths resolved via Hydra absolute path
- F (grid explosion control):
- G (bloat/cleanup):

## Notes / Risks
- ClearML Dataset 作成は `integrations/clearml/dataset.py` に閉じ込める（coreに入れない）。

## Next Improvements (Codex MUST write)
- Add optional encoding/sep handling for CSV input
- Add schema validation for required columns when target_col is known

## RESULT
- NONCE: N003-20251230-2257-7b1b
- RESULT: DONE
- Verification: `python -m tabular_analysis.cli.dataset_register run.clearml.enabled=false data.local_path=data/example.csv` (pass); `CLEARML_OFFLINE_MODE=1 CLEARML_CACHE_DIR=/Users/kawahito/Desktop/ml_polyrepo_workspace_v1/ml-solution-template/usecase/tabular-analysis/outputs/clearml_cache python -m tabular_analysis.cli.dataset_register run.clearml.enabled=true data.local_path=data/example.csv` (pass)
- Evidence (files/commands): outputs/dataset_register/{schema.json,head.csv,debug_samples.jsonl,manifest.json,config_effective.yaml,config_full.yaml}
- Next Improvements: optional CSV encoding/sep config; schema validation when target_col specified
- Files changed: src/tabular_analysis/flows/dataset_register.py, src/tabular_analysis/integrations/clearml/dataset.py
