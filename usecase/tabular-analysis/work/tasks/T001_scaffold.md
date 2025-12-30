# Task 001: 基本骨組みの確定（CLI/パッケージ/Docs最小）

Status: done  
Priority: P0

## Goal
tabular-analysis を **新規実装**するための最小骨組みを確定し、Codexが迷わず実装できる状態にする。

## Scope
### In scope
- src/tabular_analysis の import が通る
- CLIエントリポイント（pipeline/dataset_register/preprocess/train/infer/leaderboard）が Hydra で起動する
- docs の契約（特に ClearML UI契約）を参照できる
- 不要ファイルを増やさない（既存のモノリポ構成は採用しない）

### Out of scope
- 学習アルゴリズムの実装（次タスク）
- ClearML連携の実装（T005以降）

## Contracts (must follow)
- `AGENTS.md`
- `docs/01_POLYREPO_INTENT.md`
- `docs/03_CLEARML_UI_CONTRACT.md`

## Depends on
None

## Steps
1. 既存の skeleton（本フォルダ）を確認し、重複・無駄があれば削減してから進める
2. CLIが `python -m tabular_analysis.cli.pipeline` で起動し、NotImplementedError を出すことを確認
3. README のコマンドが現実的か確認し、必要なら README も修正
4. このタスクの最後に `RESULT: DONE` と Verification を必ず書く

## Acceptance Criteria
- [ ] 全CLIが Hydra を読み込み起動する（NotImplementedError で停止して良い）
- [ ] docs/03_CLEARML_UI_CONTRACT.md の方針が README から辿れる
- [ ] 不要なディレクトリ/ファイルを増やしていない

## Verification
- `python -c "import tabular_analysis; import tabular_analysis.cli.pipeline"`
- `python -m tabular_analysis.cli.pipeline --help`


## Platform reuse checklist (Codex MUST fill)
- Reused from ml-platform:
  - None in scaffold (scan only; no platform APIs invoked yet)
- Missing in ml-platform / implemented in solution:
  - None in this task (no new utilities added)
- TODO candidates to move to platform:
  - ClearML task/UI helpers if platform remains empty (planned for T005+)

## Risks addressed (Codex MUST fill; map to docs/09_RISKS_AND_MITIGATIONS.md)
- A (traceability): Not yet (manifest/properties planned in T005+)
- B (leaderboard target selection): Not yet (leaderboard tasks planned in T009/T010)
- C (comparability/leak/skew): Not yet (preprocess/train/infer planned in T004/T006/T008)
- D (ClearML UI hygiene): Partial (README points to UI contract; no logging yet)
- E (local/agent/clone): Not yet (agent/clone support planned in T012)
- F (grid explosion control): Not yet (pipeline grid planned in T011)
- G (bloat/cleanup): Addressed by keeping scaffold minimal and cleaning unused imports

## Notes / Risks
- この時点では実装はしない。骨組みの整合だけを取る。

## Next Improvements (Codex MUST write)
- Implement registry extension points for preprocess/model/metrics (T002)
- Build dataset_register local-first task and artifacts (T003)
- Add ClearML integration core with UI contract compliance (T005)

## RESULT
- NONCE: 33846c0bf7e44f32a8e52d3f41dba2b0
- RESULT: DONE
- Evidence (files/commands):
  - work/runs/_platform_scan.txt
  - src/tabular_analysis/flows/preprocess.py (NotImplementedError message)
  - src/tabular_analysis/registry/models.py (type hint)
  - conf/pipeline.yaml (pipeline output dir)
  - registry/README.md (registry pointer)
  - python -c "import tabular_analysis; import tabular_analysis.cli.pipeline"
  - python -m tabular_analysis.cli.pipeline --help
- Verification: python -c "import tabular_analysis; import tabular_analysis.cli.pipeline" (ok); python -m tabular_analysis.cli.pipeline --help (ok)
- Next Improvements:
  - Implement registry extension points for preprocess/model/metrics (T002)
  - Build dataset_register local-first task and artifacts (T003)
  - Add ClearML integration core with UI contract compliance (T005)
- Files changed:
  - conf/pipeline.yaml
  - registry/README.md
  - src/tabular_analysis/flows/preprocess.py
  - src/tabular_analysis/registry/models.py
  - work/runs/_platform_scan.txt
  - work/tasks/T001_scaffold.md
