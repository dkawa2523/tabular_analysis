# Artifact 契約（ファイル名・中身）

この契約は「後から見返しても再現できる」「非DSが迷わない」ための最低限です。

## 共通
- `config_effective.yaml`: タスクが実際に使った設定（該当部分のみ）
- `manifest.json`: 入力ID/出力ID/versions
- `summary.md`: 人間が読む要約

## preprocess
- `preprocess_bundle.joblib`
- `recipe.json`（構造化）
- `preprocess_summary.md`（カテゴリ別に記載）

## train
- `metrics.json`
- `cv_results.csv`
- `model.joblib`（local）
- `feature_importance.csv`（可能なら）

## infer
- mode別:
  - single: `single_input.json`, `single_output.json`
  - batch: `predictions.csv`
  - optimize: `trials.csv`, `best_solution.json`

## leaderboard
- `leaderboard.csv`
- `selection_rationale.md`
- `inputs_task_ids.json`

