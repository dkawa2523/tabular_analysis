# S48_PIPELINE_INDEPENDENT_TASKS: pipelineは接着（独立タスクを繋ぐ）

## 目的
- preprocess/train/infer/leaderboard を単体実行可能に保ちながら、一括評価も可能にする

## やること手順
1. pipeline は config を受け取るが、各タスクへ渡すときは **部分抽出**
2. task_id の収集と受け渡しを統一
3. pipeline は “独立タスク” を増殖させない（ロジックをタスク側へ寄せる）
4. ClearML PipelineController は後から追加（local-first）

## 事故りやすい点
- pipeline が巨大化し、タスクが空洞化する
- full config connect に戻る

## DoD
- pipeline無しでも全タスクが動く
- pipelineは task_id を正しく渡して leaderboard を実行できる

