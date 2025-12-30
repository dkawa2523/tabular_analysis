# 将来拡張ガード（multi-target / DL / image/timeseries）

このユースケースは将来の事例軸になるため、次の拡張を想定して境界を守ること。

## 1) multi-target（多次元目的変数）
- `core/data_io` は y を (n, k) を許容する（今は single-target を先に実装）
- metrics は target ごとの集約ルールを明記（mean/weightedなど）
- plots は target 次元の扱いを設計（上位次元だけ表示など）

## 2) deep learning / image
- `registry/models.py` は backend が sklearn 以外でも登録できる設計にする
- dataset 形式（files/folders）でも `dataset_register` が扱えるようにする
- ClearML Dataset の “フォルダデータ” 登録を想定

## 3) timeseries
- split 戦略（time-based split）を `train.split.*` に追加できるようにする
- leakage ガード（未来情報）を doctor に組み込む

## 4) 境界
- core/ は ClearML に依存しない（純粋ロジック）
- integrations/clearml/ に UI/ログの責務を閉じ込める
- registry は拡張点を一意にする（編集箇所を散らさない）

