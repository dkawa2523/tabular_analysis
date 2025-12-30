# ClearML UI 契約（最重要）

目的：非DSが ClearML 上で「迷わず辿れる」こと。  
**HyperParameters は “そのタスクの設定だけ”** に限定し、他情報は Properties/Artifacts に分離します。

---

## 共通ルール
### HyperParameters
- `task.connect()` するのは **該当タスクの config 部分のみ**
- pipeline の設定全体、他タスクの設定は **絶対に connect しない**
- 例：train タスク → `train.*` と `model.*` と `data.*(dataset参照のみ)` だけ

### User Properties（一覧で見るため）
- `usecase_id`
- `dataset_id`, `preprocessed_dataset_id`
- `model_name`, `model_id`
- `primary_metric`, `primary_score`
- `run_mode`（local/agent）
- `code.repository`, `code.branch`, `code.entry_point`（UI clone 用）

### Artifacts（長文/再現用）
- `config_effective.yaml`（このタスクで実際に使った設定のみ）
- `manifest.json`（入力→出力の関係とバージョン）
- `summary.md`（人間が読む要約）
- `debug_samples.jsonl`（少量サンプル）

### Plots（意思決定用の最小セット）
- preprocess: 分布のbefore/after（必要最小）
- train: 予測vs真値、残差、（可能なら）特徴量重要度
- leaderboard: モデル比較（上位Nだけ）、推奨モデルの明示

### Debug Samples（探索用）
- 入力の先頭数行（匿名化/列制限ルールを守る）
- 推論の例（single/batchの小サンプル）

---

## タスク別ガイド

### dataset_register
- HyperParameters: `data.local_path`, `data.format`
- Properties: `dataset_id`, `n_rows`, `n_cols`
- Artifacts: `schema.json`, `head.csv`, `manifest.json`
- Plots: なし（原則）
- Debug Samples: head/tail

### preprocess
- HyperParameters: `preprocess.*` + `data.dataset_id`
- Properties: `preprocessed_dataset_id`, `preprocess_name`
- Artifacts:
  - `preprocess_bundle.joblib`
  - `preprocess_summary.md`（カテゴリ別：入力/目的変数/欠損/スケール等）
  - `recipe.json`
- Plots: before/after分布（必要最小）
- Debug Samples: 変換前後の少量比較

### train
- HyperParameters: `model.*`, `train.*`, `data.dataset_id`
- Properties: `model_id`, `model_name`, `primary_metric`, `primary_score`
- Artifacts:
  - `metrics.json`
  - `cv_results.csv`
  - `model.joblib`（local時）
- Plots: pred-vs-true, residuals, (可能なら) importance
- Debug Samples: 予測例（数件）

### infer
- HyperParameters: `infer.*`, `model.model_id`
- Properties: `mode`, `n_outputs`, `output_path`
- Artifacts:
  - `predictions.csv` / `best_solution.json` など mode別
- Plots: optimize の収束/履歴のみ（必要最小）
- Debug Samples: 入力→出力の例

### leaderboard
- HyperParameters:
  - `leaderboard.task_ids`（基本）
  - optional: `leaderboard.filter.project`, `leaderboard.filter.tags`
- Properties: `recommended_model_id`, `recommended_model_name`
- Artifacts:
  - `leaderboard.csv`
  - `selection_rationale.md`
- Plots:
  - metric比較棒グラフ（上位N）
  - 前処理×モデルのヒートマップ（可能なら）

---

## 注意（最重要）
- 「学習サマリー＝親タスク」ではありません。  
  **leaderboard は独立タスク**であり、trainタスクとは親子リンクしません。

