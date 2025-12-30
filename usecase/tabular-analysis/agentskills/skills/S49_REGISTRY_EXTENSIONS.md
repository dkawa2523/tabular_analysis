# S49_REGISTRY_EXTENSIONS: registry を拡張点に固定する

## やること手順
1. 新しいモデル/前処理/指標は必ず registry に登録
2. 呼び出し側は name を受け取り registry から生成する
3. conf/ に対応する config を追加
4. docs/05_REGISTRY_EXTENSION.md を更新

## 事故りやすい点
- 実装が分散して編集箇所が増える
- 特定用途のif/elseが core に増える → registryへ戻す

## DoD
- 追加機能の差分が registry + conf で完結

