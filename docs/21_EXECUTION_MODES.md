# 実行モード（Local / Agent / UI Clone）

## 1) Local mode（開発・デバッグ）
- `run.clearml.enabled=false`
- ローカルで核処理を実行し、結果をファイルに出す

## 2) ClearML Logging mode（ローカル起動→ClearMLにログ）
- `run.clearml.enabled=true`
- `Task.init` でタスクを作成し、Artifacts/Plots/Properties を記録

## 3) Agent mode（enqueue）
- `enqueue=true` のとき `task.execute_remotely(queue_name=...)`
- Agentは git repo を clone して実行（もしくは `set_script`）

## 4) UI Clone mode（ClearML UIから実行）
- `task.set_script(repository/branch/entry_point/working_dir)` を設定できる
- これにより “ClearML上でリポジトリURL設定” が容易になる
