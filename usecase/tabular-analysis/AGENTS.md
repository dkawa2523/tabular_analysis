# AGENTS.md (Codex向け: tabular-analysis)

このフォルダは **大規模実装** ですが、必ず「着実に」進めます。  
Codexは以下を厳守してください。

## 最重要ルール
1) **独立タスク**: preprocess/train/infer/leaderboard は親子タスクにしない（Task parent/child link を作らない）
2) **UI契約**: HyperParameters は “そのタスクの設定だけ”。他は Properties/Artifacts に分離
3) **ローカルファースト**: まず `run.clearml.enabled=false` で動かし、その後 ClearML on を実装
4) **registryが拡張点**: 新しい前処理/モデル/指標は registry に追加し、呼び出し側は増やさない
5) **ファイル増殖禁止**: 追加ファイルは「必要最小限」。複雑化の兆候があれば先に整理する
6) **DONE条件**: work/tasks の `RESULT: DONE` を書き、Verificationを全て通すまでタスクを完了しない

## タスク実行の作法
- 1タスクでやりきれない場合は、**同じタスク内で分割サブチェックリスト**を増やして完了させる
- 中途半端な実装で次タスクに進まない
- 失敗したら原因を `Fix Plan` に書き、次の実行で確実に修正する

## 出力（各タスクで必須）
- `work/tasks/Txxx_*.md` の末尾に必ず追記:
  - `RESULT: DONE`
  - `Verification: <実行したコマンドと結果>`
  - `Next Improvements:`（次タスクが実装しやすい改善案を箇条書き）
  - `Files changed:`（主要ファイル）

## 参照ドキュメント
- `docs/03_CLEARML_UI_CONTRACT.md`（最優先）
- `docs/07_PIPELINE_CONTRACT.md`（独立タスクの接着）



## 追加ルール（v4）
- **ml-platform 再利用**: 同等のユーティリティを新規実装する前に `docs/10_PLATFORM_TEMPLATE_USAGE.md` に従って platform を探索し、再利用すること。
- **想定課題の潰し込み**: `docs/09_RISKS_AND_MITIGATIONS.md` のA〜Gを参照し、各タスクで潰したリスクを task md の `Risks addressed:` に必ず記載すること。
- **比較可能性のガード**: `processed_dataset_id` / `split_hash` / `recipe_hash` を比較の鍵として扱い、leaderboard/pipelineで混在があれば警告または除外すること。
