# Usecase Guide（非DS向け導線）

## 目的
- dataset_id を入力して Pipeline を実行し、結果を見てモデルを選ぶ

## ClearMLで見る順番
1. `MFG/<usecase>/99_pipeline` の Pipeline タスクを開く
2. step の `train_parent`（Training Summary）へ移動
3. `Plots` の `01_leaderboard_table` / `02_topk_bar` を見る
4. `User Properties` の `recommended_model_id` を確認
5. 推論: `infer_single` or `infer_batch` を実行（model_idを入力）

## 間違えないためのルール
- 親タスクは比較だけ（詳細は子タスクを見る）
- HyperParametersは“そのタスクに関係するものだけ”
