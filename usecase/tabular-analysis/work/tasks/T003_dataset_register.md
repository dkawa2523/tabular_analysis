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
- ClearML Dataset 作成は `integrations/clearml/dataset.py` に閉じ込める（coreに入れない）。

## Next Improvements (Codex MUST write)
- (write suggestions for next tasks)

## RESULT
- NONCE: 
- RESULT: (TODO)  # Must be set to DONE to complete task
- Evidence (files/commands):
