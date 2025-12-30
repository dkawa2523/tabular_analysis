# 想定課題と対応策（tabular-analysis）

この文書は、仕様どおりに運用したときに起きがちな課題と、その対応策（実装ガード/運用ルール/タスク化）をまとめたものです。
Codexは実装中にこの文書を参照し、**再発しやすい事故を設計で潰す**こと。

---

## A. 独立タスク化で「関連が見えない」
### 症状
- preprocess/train/infer/leaderboard が親子でないため、ClearML UI で関連が追いづらい
- どれが同一実行セット（grid）かわからない

### 対応策（必須）
- **共通User Properties** を全タスクに付与：
  - `usecase_id`, `process`, `schema_version`, `code_version`, `platform_version`, `grid_run_id`(任意)
- **manifest.json** を全タスクのArtifactとして必須（inputs/outputs/hashesを含む）
- pipelineは **pipeline_run.json** を必須Artifact（step_task_ids / train_task_ids / leaderboard_task_id）

---

## B. leaderboard の集計対象指定が重い／誤りやすい
### 症状
- task_id を手で集めるのが面倒、間違える

### 対応策（必須）
- pipeline実行時は **train_task_ids を自動受け渡し**
- leaderboard は以下を実装：
  - 入力：`task_ids`（基本）
  - オプション：`query.project`, `query.tags` で探索（ただし最終的に解決した task_id を Artifact に保存）
- leaderboard は **比較可能性チェック** を必須：
  - `processed_dataset_id` が混在 → warning or exclude
  - `split_hash` が混在 → compare不可（exclude推奨）
  - `metric.primary` が一致しない → compare不可（exclude推奨）

---

## C. 比較可能性の崩壊（split/seed/前処理fitの揺れ、leak/skew）
### 症状
- trainが勝手にsplitを再生成
- preprocessのfitとinferのtransformがズレる
- target変換の逆変換漏れ

### 対応策（必須）
- splitは preprocess が生成し、train は **splitを再利用**（再生成禁止）
- preprocess bundle（features+target変換）を `bundle.joblib` として保存
- trainは `model_bundle/` に **bundleとschemaを同梱** し、inferはそれを読む（再fit禁止）
- inferは **逆変換が必要な場合は必ず元スケールで出力**

---

## D. ClearML UI 汚染（HyperParameters/Plotsの情報過多）
### 症状
- pipeline全設定がHyperParametersに混ざる
- plotが多すぎて非DSが判断できない

### 対応策（必須）
- HyperParameters は **そのタスクの入力設定だけ** を connect（full config禁止）
- Plotsは番号プレフィックスで順序固定：`01_`, `02_`...
- 重い可視化（SHAP等）は **configでON時のみ** 生成
- Debug Samplesは少量、データ本体はArtifactsへ

---

## E. localでは動くがAgent/cloneで動かない
### 症状
- 依存/entry_point/working_dirズレ、trusted dir 問題、queue未監視

### 対応策（必須）
- `tools/doctor.py` を必須化：
  - import/依存
  - ClearML接続
  - queue存在
  - clone_template_task_id の存在（clone運用時）
- `run.clearml.execution = local|agent|clone` を単一キーで切替
- clone運用は `set_script(repo/branch/entry_point/working_dir)` を config化し、**UIからcloneしても同じ**を担保

---

## F. gridでタスク爆発
### 症状
- タスク数が増え、どれが今回の実行か不明

### 対応策（推奨）
- pipelineは `grid_run_id` を生成し、全タスクに tag `grid:<id>` を付与
- pipeline_run.json を保存し、「今回の集合」を一発で辿れる

---

## G. フォルダ/ファイル増殖、拡張点が不明
### 症状
- どこを触れば拡張できるか分からない
- 使っていないコードが残る

### 対応策（必須）
- 拡張は registry + conf/group を基本にする（別ディレクトリ増やさない）
- タスク内で不要ファイルは削除（削除できない場合は理由とTODO）
- `tools/cleanup_repo.py` で dry-run 可能な掃除を提供

---

## Codexへの指示（実装時の強制チェック）
各タスク完了時に task md に以下を必ず記載：
- `Risks addressed:`（上のA〜Gのどれを潰したか）
- `Evidence:`（どのArtifact/Properties/Plotsで担保したか）
- `Next Improvements:`（次タスクに渡す改善案）
