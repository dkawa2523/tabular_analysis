# S45 Platform reuse & adapter strategy

## 目的
- solution内に「platformと同じもの」を作らない
- platform/solution分離の意図を守り、長期保守コストを下げる

## やること手順
1. `tools/platform_scan.py` を実行して platform の利用可能ユーティリティを把握
2. 同等機能が存在する場合は、それを使う（importして呼ぶ）
3. ない場合は solution に実装してよいが、後で platform へ移管できるよう薄いラッパで作る
4. task md に「platform再利用状況」を記録
   - reused: xxx
   - missing: yyy (TODO: consider moving to platform)

## 事故りやすい点
- 似たヘルパーが乱立し、ClearMLログの仕様が揺れる
- agent/clone運用のI/Fが用途ごとにバラバラになる

## DoD
- platform の既存関数を優先使用している
- 追加した場合は移管候補が明記されている
