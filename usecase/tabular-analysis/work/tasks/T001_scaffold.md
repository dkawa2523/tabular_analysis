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
  - None in this scaffold task (platform_scan only; no clearml utils available).
- Missing in ml-platform / implemented in solution:
  - None in this task (ClearML/task utils to be evaluated in later tasks).
- TODO candidates to move to platform:
  - None yet.

## Risks addressed (Codex MUST fill; map to docs/09_RISKS_AND_MITIGATIONS.md)
- A (traceability): N/A in scaffold (no artifacts/manifest yet).
- B (leaderboard target selection): N/A in scaffold (no leaderboard logic yet).
- C (comparability/leak/skew): N/A in scaffold (no data flow yet).
- D (ClearML UI hygiene): README references UI contract; scaffold keeps CLI tasks isolated.
- E (local/agent/clone): N/A in scaffold (execution modes to be added later).
- F (grid explosion control): N/A in scaffold (pipeline logic later).
- G (bloat/cleanup): Kept existing layout; no new dirs/files beyond minimal edits.

## Notes / Risks
- この時点では実装はしない。骨組みの整合だけを取る。

## Next Improvements (Codex MUST write)
- Implement registry extensions in `src/tabular_analysis/registry/*` (T002).
- Implement dataset_register local-first flow (T003).
- Implement ClearML integration core (T005).

## RESULT
- NONCE: 3406554ddb644b9aa3083e25efab3f40
- RESULT: DONE
- Evidence (files/commands):
  - src/tabular_analysis/cli/_common.py (centralized Hydra config path).
  - src/tabular_analysis/cli/*.py (use shared config path).
- Verification:
  - `.venv/bin/python -c "import tabular_analysis; import tabular_analysis.cli.pipeline"` (ok)
  - `.venv/bin/python -m tabular_analysis.cli.pipeline --help` (ok)
- Next Improvements:
  - Implement registry extensions in `src/tabular_analysis/registry/*` (T002).
  - Implement dataset_register local-first flow (T003).
  - Implement ClearML integration core (T005).
- Files changed:
  - src/tabular_analysis/cli/_common.py
  - src/tabular_analysis/cli/dataset_register.py
  - src/tabular_analysis/cli/preprocess.py
  - src/tabular_analysis/cli/train.py
  - src/tabular_analysis/cli/infer.py
  - src/tabular_analysis/cli/leaderboard.py
  - src/tabular_analysis/cli/pipeline.py
  - work/tasks/T001_scaffold.md
