# S40_ARCHITECTURE: 境界を守り、増殖を防ぐ

## やること手順
1. 境界確認:
   - `core/` は ClearML 依存禁止
   - `integrations/clearml/` に UI/ログ責務を閉じ込める
   - 拡張点は `registry/` に固定
2. 新ファイル追加前に「既存に置けない理由」を書く（最小化）
3. 設計がブレたら `docs/` を先に更新し、契約を固定してから実装

## 事故りやすい点
- 便利だからと task側に ClearML API 直書きが増える
- config を全 connect して HyperParameters が汚染される

## DoD
- 主要責務が境界に沿って配置されている
- 追加ファイルが最小限で、理由が説明できる

## よくある差分
- 例外処理の共通化は platform に寄せるか、solutionで一箇所にまとめる
