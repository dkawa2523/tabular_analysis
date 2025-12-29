# S60 ClearML pipelines/orchestration

## やること手順
1. Pipeline は “司令塔” で処理を持たない
2. step は独立タスク（単体実行と同一）
3. parameter handoff を明確化（dataset_id, model_id）
4. `reuse_last_task_id=False` を固定
5. queue/agent が無い場合の失敗を分かりやすく
6. Solution repo URL を `task.set_script` で設定可能に（UI起動用）

## DoD
- step_task_ids.json が残る
- ClearML UI上でDAGが追える
