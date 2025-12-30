# Usecase Guide（非DS向け導線）

## 目的
- dataset_id を入力して Pipeline を実行し、比較結果から推奨モデルを選ぶ
- 推奨 model_id で推論を実行する

## 必要な入力
- usecase_id: `MFG/<usecase_id>/...` の project prefix
- dataset_id: Pipeline/各タスクの共通キー
- model_id: `train_parent` の `recommended_model_id` を利用

## ClearMLでの進め方（最短導線）
1. `MFG/<usecase_id>/99_pipeline` の `pipeline` を実行（dataset_id を入力）
   - 推論まで実行する場合は `pipeline.include_infer=true` と `pipeline.infer_model_id` / `pipeline.infer_mode` を設定
   - stepタスクは `MFG/<usecase_id>/00_dataset` / `10_preprocess` / `20_train_parent` / `30_infer` に作成される
2. Pipeline の Step から `train_parent` を開く（Training Summary）
3. `Plots` の `01_leaderboard_table` / `02_topk_bar` を確認
4. `User Properties` の `recommended_model_id` を確認
5. 詳細確認が必要な場合は `MFG/<usecase_id>/21_train_model` の子タスクを開く
6. 推論は `MFG/<usecase_id>/30_infer` の `infer` を実行（infer.model_id に推薦値）

## 間違えないためのルール
- 親タスクは比較だけ（詳細は子タスクを見る）
- HyperParametersは“そのタスクに関係するものだけ”
- Full config は Artifact `config_full.yaml` を参照
