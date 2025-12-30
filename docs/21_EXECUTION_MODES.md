# 実行モード（Local / Agent / UI Clone）

## 共通設定キー
|用途|設定|メモ|
|---|---|---|
|ClearML切替|`run.clearml.enabled`|false=ClearMLなし|
|Agent実行|`run.clearml.enqueue` / `run.clearml.queue_name`|trueで`task.execute_remotely`|
|タグ|`run.clearml.tags`|Taskに付与|
|UI Clone|`run.clearml.script.*` / `run.clearml.ui_clone.*`|repository + entry_point 必須|
|Pipeline step 実行|`pipeline.run_steps_locally`|pipeline CLIのみ|

## 1) Local mode（開発・デバッグ）
- `run.clearml.enabled=false` で実行
- Pipeline CLIは ClearML専用のため、local では `dataset_register` / `preprocess` / `train_parent` / `infer` を直接実行

## 2) ClearML Logging mode（ローカル起動→ClearMLにログ）
- `run.clearml.enabled=true`
- Taskを作成して Artifacts/Plots/Properties を記録
- `run.clearml.enqueue=false` の場合はローカル実行

## 3) Agent mode（enqueue）
- `run.clearml.enqueue=true` のとき `task.execute_remotely(queue_name=...)`
- `run.clearml.queue_name` を設定
- Pipelineは `pipeline.run_steps_locally=false` で agent 実行

## 4) Pipeline mode（ClearML PipelineController）
- `src/usecase/cli/pipeline.py` が PipelineController を使用
- `pipeline.run_steps_locally=true` なら step をローカル実行
- `pipeline.run_steps_locally=false` なら ClearML Agent を要求
- Pipeline param: `dataset_id`, `infer_mode`, `infer_model_id`

## 5) UI Clone mode（ClearML UIから実行）
- `run.clearml.script.repository` / `entry_point` を指定すると `task.set_script(...)`
- `run.clearml.ui_clone.*` は script 未指定時の fallback
- `branch` / `working_dir` も指定可能（対応していない場合は自動で除外）

## Cleanup（生成物の掃除）
- Dry-run: `python tools/cleanup_repo.py --repo . --dry-run`
- 実削除: `python tools/cleanup_repo.py --repo . --apply`
- 対象: `outputs/`, `multirun/`, `work/runs/`, `.clearml_cache/` など
