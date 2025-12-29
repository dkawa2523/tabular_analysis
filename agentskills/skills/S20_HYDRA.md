# S20 Hydra config conventions

## やること手順
1. task root を分ける（preprocess/train/infer/pipeline）
2. seed/eval/data は共通に寄せ、taskに注入
3. ClearML HyperParameters に出す項目は task固有に限定
4. `config_full.yaml` は Artifact 保存（再現性）

## 事故りやすい点
- config全体をtask.connectしてHyperParametersが汚染される
- Solution側でPlatformと同名の設定が増え、意味が衝突する

## DoD
- `conf/` が読みやすい（taskごと）
- override例がある
- HyperParametersの設計が docs/02 と一致
