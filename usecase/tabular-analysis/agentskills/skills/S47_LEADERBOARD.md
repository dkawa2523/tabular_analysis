# S47_LEADERBOARD: 独立タスクの集計・比較

## 目的
- train タスク群を横断して比較し、推奨モデルを明確にする

## やること手順
1. 入力は task_id list を基本にする
2. 各taskから取得する “最低限情報” を契約化:
   - model_id, model_name
   - preprocess_name（あれば）
   - primary_metric, primary_score
3. DataFrame化 → rank
4. Artifacts:
   - leaderboard.csv
   - selection_rationale.md
5. Plots:
   - 上位N棒グラフ
   - （可能なら）前処理×モデルのヒートマップ
6. Properties:
   - recommended_model_id/name/score を必ず

## 事故りやすい点
- 親子リンクに戻してしまう（禁止）
- 取得元（scalar/artifact/property）が揺れて壊れる → 契約を固定

## DoD
- 非DSが leaderboard だけ見て意思決定できる

