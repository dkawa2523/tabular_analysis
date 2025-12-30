# pipeline 契約（独立タスクをどう繋ぐか）

## 原則
- pipeline は “接着” である
- 各タスクは単体で実行できる（pipeline無しでも動く）
- pipeline は **task_id の受け渡し**で連結する

## ローカル実行（最初に必ず通す）
- pipeline は同一プロセスで順次 `cli.*` を呼び出して良い
- その場合も、ClearML enabled 時は各タスクが独立 Task として記録される

## ClearML pipeline 実行（後から有効化）
- PipelineController でステップを定義しても良いが、
  *train/preprocess を「子タスク」としてリンクしない*（リンクは optional）
- 実運用では、template task を clone して enqueue する形にする
- pipeline は最後に leaderboard に task_id list を渡す

## leaderboard の対象指定
- 基本: `leaderboard.task_ids=[...]`
- optional:
  - `leaderboard.filter.project=...`
  - `leaderboard.filter.tags=[...]`
- pipeline 実行時は task_id を自動収集し、ユーザー指定不要

