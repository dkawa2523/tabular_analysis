# S70_TESTING: smoke/doctor で壊れない開発

## やること手順
1. 小さな合成データで E2E を通す（preprocess→train→leaderboard→infer）
2. ClearML off で必ず通す
3. on は optional（環境があれば）

## 事故りやすい点
- テスト無しで進んで最後に壊れる

## DoD
- `python tools/smoke.py` が通る

