# ml-solution-template — Usecase Solution Repo (Polyrepo)

これは **用途別リポジトリ（Solution）のテンプレート**です。  
`ml-platform` を依存として使い、用途固有の差分（設定/registry/pipeline）だけ実装します。

## ユーザー導線（非DS）
|目的|ClearMLプロジェクト|入力/見る場所|
|---|---|---|
|Pipeline実行|`MFG/<usecase_id>/99_pipeline`|`dataset_id`, `pipeline.include_infer`, `pipeline.infer_model_id`, `pipeline.infer_mode` / Step一覧|
|Training Summary|`MFG/<usecase_id>/20_train_parent`|Plots `01_leaderboard_table`, `02_topk_bar` / User Properties `recommended_model_id`|
|詳細診断|`MFG/<usecase_id>/21_train_model`|モデル別の詳細Plots/Artifacts|
|推論|`MFG/<usecase_id>/30_infer`|`infer.model_id`, `infer.mode` / Artifact `preds.csv`|

```mermaid
flowchart LR
  A[dataset_id] --> B[Pipeline<br/>MFG/<usecase_id>/99_pipeline]
  B --> C[dataset_register<br/>00_dataset]
  C --> D[preprocess<br/>10_preprocess]
  D --> E[train_parent<br/>20_train_parent]
  E --> F[train_model (child)<br/>21_train_model]
  E --> R[recommended_model_id]
  R --> G[infer (optional)<br/>30_infer]
```

## このSolutionが持つもの
- `conf/` : Hydra設定（用途固有のデフォルト/override）
- `src/usecase/` : pipeline定義・registry拡張・入口CLI
- `docs/` : Platform契約のスナップショット＋用途固有の運用手順
- `work/` : Codexタスク（用途固有に必要な実装）

## Local実行とClearML実行
- Local: `run.clearml.enabled=false`（PipelineはClearML専用のため step CLIを実行）
- ClearML Logging: `run.clearml.enabled=true`（Task/Artifacts/Plots）
- ClearML Agent: `run.clearml.enqueue=true` + `run.clearml.queue_name`
- ClearML UIから: `run.clearml.script.*` / `run.clearml.ui_clone.*` で `task.set_script(...)`

---

## セットアップ
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements/base.txt
```

### Platform依存（開発時）
開発中は、Platformを editable install するのが簡単です:

```bash
pip install -e ../ml-platform
```

（本番では `ml-platform==X.Y.Z` にpin）

### ClearML初回設定
```bash
clearml-init
```

### Codex selfcheck / loop
```bash
bash tools/codex_loop/selfcheck_codex_exec.sh
python tools/codex_loop/run.py --repo . --once
python tools/codex_loop/run.py --repo .
```
