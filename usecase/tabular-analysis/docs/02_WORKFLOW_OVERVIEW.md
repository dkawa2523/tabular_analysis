# ワークフロー全体像（tabular-analysis）

## 概要
- データ登録（任意）: CSV/Parquet → ClearML Dataset
- 前処理: dataset_id(or local) → 前処理済みDataset（bundle+summary付き）
- 学習: dataset_id → model_id（ClearML Model Registry）+ metrics + plots
- 推論: model_id + mode → outputs
- leaderboard: train_task_ids を集約 → 比較/推奨

## Mermaid（タスクは独立、親子無し）
```mermaid
flowchart LR
  A[(Raw Dataset)] -->|dataset_register (optional)| D[(ClearML Dataset)]
  D -->|preprocess (N patterns)| P1[(Preprocessed Dataset #1)]
  D -->|preprocess (N patterns)| P2[(Preprocessed Dataset #2)]
  P1 -->|train (M models)| T11[Train Task]
  P1 -->|train (M models)| T12[Train Task]
  P2 -->|train (M models)| T21[Train Task]
  P2 -->|train (M models)| T22[Train Task]
  T11 -->|task_id list| L[leaderboard]
  T12 -->|task_id list| L
  T21 -->|task_id list| L
  T22 -->|task_id list| L
  L -->|recommended_model_id| I[infer (single/batch/optimize)]
```

## I/O（最小）
| Task | Inputs | Outputs |
|---|---|---|
| dataset_register | local_path | dataset_id |
| preprocess | dataset_id or local_path, preprocess cfg | preprocessed_dataset_id, bundle |
| train | dataset_id, model cfg, eval cfg | model_id, metrics, plots |
| infer | model_id, mode cfg | preds / report |
| leaderboard | train_task_ids (or filters) | leaderboard.csv, recommended_model_id |

