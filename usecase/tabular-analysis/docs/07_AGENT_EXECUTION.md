# ClearML Agent 実行（後で検証するための設計）

ローカルで動作確認した後に、ClearML Agent で同じタスクを動かすための規約です。

## 1) UI clone / template task 方式
- 各タスクは `run.clearml.code.*` を持つ
- `run.clearml.code.set_script=true` のとき、実行時に `task.set_script(...)` を設定する
  - repository / branch / entry_point / working_dir を明示し、UI 上で追跡しやすくする

## 2) 実行キュー
- `run.clearml.queue` を設定し、`task.execute_remotely(queue)` を利用可能にする（タスク単体）
- pipeline の場合は `PipelineController` または clone+enqueue を使用

## 3) テンプレートタスクの作り方（運用）
- ClearML UI で各タスクを一度ローカル実行して “テンプレ候補” を作成
- その task_id を設定に控える
- pipeline からは task_id を clone して実行

