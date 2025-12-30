# registry 拡張ガイド（開発者向け）

このユースケースの拡張点は **registry** に集約します。  
開発者が「どこを触ればよいか」迷わないことが最重要です。

## 1) 前処理を追加する
編集: `src/tabular_analysis/registry/preprocessors.py`

- `register_preprocessor(name: str, factory: Callable)`
- `build_preprocessor(cfg) -> Transformer` を増やす

追加後:
- `conf/preprocess/<name>.yaml` を作る
- `docs/03_CLEARML_UI_CONTRACT.md` に plot/debug の扱いを追記（必要なら）

## 2) モデルを追加する
編集: `src/tabular_analysis/registry/models.py`

- `register_model(name: str, factory: Callable)`
- 学習に必要な前処理や feature importance などは `core/training.py` と `core/plots.py` に実装

追加後:
- `conf/model/<name>.yaml` を作る

## 3) 指標を追加する
編集: `src/tabular_analysis/registry/metrics.py`

- `METRICS[name] = callable(y_true, y_pred)`

## 4) 可視化を追加する
編集: `src/tabular_analysis/core/plots.py`

- 追加してよい plot と、親（leaderboard）に出してよい plot を区別すること
- heavy plot（SHAP 等）は train タスクに限定し、leaderboard は最小にする

