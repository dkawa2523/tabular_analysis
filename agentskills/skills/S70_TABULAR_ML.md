# S70 Tabular ML workflow

## やること手順
1. schema（features/target）を明確にする
2. 前処理bundle（fit/transform + inverse）を作る
3. split/CV/seed を評価規約に従って固定
4. 子タスクで詳細評価、親タスクで集計
5. 推論では学習と同じbundleを必ず使う
6. usecase_id を常にログ（Properties/Artifacts）に出す

## DoD
- predsとmetricsがArtifactsに残る
- 逆変換が必要なら適用される
