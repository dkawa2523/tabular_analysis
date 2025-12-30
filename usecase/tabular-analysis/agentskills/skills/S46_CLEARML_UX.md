# S46_CLEARML_UX: ClearML UI 契約を守る

## 参照
- `docs/03_CLEARML_UI_CONTRACT.md`

## やること手順
1. Task.init:
   - `auto_connect_arg_parser=False` 相当で勝手な connect を防ぐ
2. HyperParameters:
   - **そのタスクの設定だけ**を `connect` する
   - pipeline全体/他タスク設定は connect しない
3. Properties:
   - 一覧で比較できるキーを揃える（dataset_id/model_id/primary_score 等）
4. Artifacts:
   - `config_effective.yaml`, `manifest.json`, `summary.md` は必ず
5. Plots:
   - leaderboardは最小、heavy plotはtrainへ
   - タイトルに番号prefix（`01_...`）を付け順序を安定化
6. Debug samples:
   - 先頭数行/予測例など「少量」で十分

## 事故りやすい点
- full config を connect して HyperParameters が汚染
- 見るべきplotが多すぎて非DSが迷う

## DoD
- UI上で役割と結果が誤認されない配置になっている

## よくある差分
- 推奨モデルの情報は leaderboard の Properties に集約（trainに入れすぎない）
