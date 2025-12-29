# S40 ClearML Task UI design

## やること手順
1. docs/02 のUI契約を読む
2. task init 時に auto_connect を抑制し、明示的に connect する
3. HyperParameters は “そのタスクの knobs” のみに絞る
4. Properties は検索に使う短い要約（usecase_id/dataset_id/model_id/score）
5. Artifacts は業務利用の成果物（CSV/JSON/Parquet）
6. Plots は最小限、prefix で順序を固定
7. Debug samples は少量で固定
8. **UI起動/Agent実行**を想定する場合、`task.set_script(...)` を config で制御

## 事故りやすい点
- 親タスクに大量プロットが集約されて見づらい
- 同一Git URLで用途が混ざり、非DSが誤認する（ポリレポで解消）

## DoD
- 仕様表（docs/02）と実装が一致
- 親/子の責務が崩れていない
