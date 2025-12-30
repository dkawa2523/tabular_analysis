# Hydra 設定規約（tabular-analysis）

## 基本
- すべての CLI は Hydra で起動する（`conf/` を参照）
- タスク別に config の責務を分離する
- pipeline config は「接着」用。preprocess/train/infer/leaderboard の config を内包するが、
  **各タスクに渡すときは該当部分だけを抽出して connect する（UI汚染防止）**

## 重要なキー
- `run.mode`: `local` / `agent` / `clearml_pipeline`（最初は local を主）
- `run.clearml.enabled`: true/false
- `run.clearml.project_root`: `MFG/<UseCase>` を推奨
- `run.clearml.code.*`: UI clone 用 script 情報（repository/branch/entry_point）

## config の構造（例）
- `data.*`
- `preprocess.*`
- `model.*`
- `train.*`
- `infer.*`
- `leaderboard.*`
- `pipeline.*`

## multi-run（組合せ評価）の扱い
- 推奨: pipeline が `pipeline.preprocess_grid` と `pipeline.models` をループして
  `preprocess` と `train` を複数回起動し、その task_id を leaderboard に渡す。
- Hydra の multirun に依存しない（オプションで後から導入可能）

