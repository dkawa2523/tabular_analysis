# polyrepo の意図（Platform / Solution の境界）

このプロジェクトは **Platform（共通基盤）** と **Solution（用途別）** を分けます。

## なぜ分けるのか
- **ClearML 上で Git URL が用途別になる** → 非DSが「何の用途のタスクか」を誤認しにくい
- 共通基盤（ClearML連携、Artifacts契約、Config規約）を **安定させる**
- ユースケース（tabular / image / timeseries / multi-target 等）は **薄い差分**で追加できる

## 何を Platform に置くべきか（不変・横断）
- ClearMLの「UI契約」実装（HyperParameters汚染防止、Properties/Artifacts/Plotsの配置）
- Dataset/Model/Task/Pipeline の薄い wrapper
- Config の共通規約（run, seed, dataset参照、artifact naming）
- “壊してはいけない契約” docs と、CI/doctor

## 何を Solution に置くべきか（用途固有）
- 前処理/特徴量/モデル/推論/可視化の「中身」
- Hydra config の具体値（デフォルトやグリッド）
- その用途の非DS向け README（見る順、操作順）
- registry の追加（モデルや前処理の登録）

## このユースケース(tabular-analysis)の方針
- **独立タスク**: preprocess/train/infer は単体で実行・再実行できる
- **leaderboardは別タスク**: task_id 群を集約して比較（親子リンクは作らない）
- **pipelineは接着**: 複数タスクを起動し、最後に leaderboard に渡すだけ

