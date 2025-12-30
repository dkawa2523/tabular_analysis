# ml-platform / 既存雛形の利用ガイド（Codex向け）

このユースケース（tabular-analysis）は **ml-platform の共通雛形・ユーティリティを再利用**して実装する。
Codexは新規に同じ機能を実装する前に、必ず platform を探索し、再利用できるものを使うこと。

## 目的
- platform/solution 分離の意図を守る（platform肥大化防止、solutionの責務を明確に）
- ClearML/Artifact/実行モード等の「共通の難所」を platform 側に集約し、solutionはドメイン差分に集中する

## 実装ルール（必須）
1. `../../../ml-platform` を探索して、以下のカテゴリのユーティリティが存在するか確認する
   - ClearML: task init, connect hparams, properties, artifacts, plots, dataset, model registry, clone, queue
   - Artifact/versioning: manifest, config hash, safe paths
   - execution modes: local/agent/clone の切替
2. 見つかった場合は **platformを優先して利用**
3. 見つからない場合は solution に実装してよいが、その際も
   - interfaceは platform 側に移せる形（薄いラッパ）にする
   - TODOとして platform 移管候補を明記

## 期待するplatform API（例：存在すれば使う）
- `ml_platform.clearml.task_factory.init_task(...)`
- `ml_platform.clearml.logging.connect_hparams_subset(task, cfg)`
- `ml_platform.clearml.logging.set_user_properties(task, props)`
- `ml_platform.clearml.logging.upload_artifacts(task, files)`
- `ml_platform.clearml.logging.log_plot(task, fig, title)`
- `ml_platform.clearml.dataset.get_dataset_local_copy(dataset_id)`
- `ml_platform.clearml.dataset.create_dataset_from_files(...)`
- `ml_platform.clearml.model.register_model(...)`
- `ml_platform.exec_modes.run_locally_or_remote(cfg, task)`

※ 実際の名前は platform 実装に合わせる。存在しない場合は探索結果を task md に記録する。

## 付録：探索手順（Codexがやる）
- `python tools/platform_scan.py` を実行し、結果ファイル `work/runs/_platform_scan.txt` を読む
- `import ml_platform` が通るか `tools/doctor_platform.py` で確認する
