# Troubleshooting（詰まったときの確認ポイント）

このユースケースは Codex で大規模開発を進める前提のため、**詰まったときに見る場所**を固定します。

---

## 1) codex_loop のログの場所

タスク実行のたびに、以下にログが保存されます。

- `work/runs/task_XXX/`
  - `prompt.txt` : Codex に渡したプロンプト（契約/スキル/タスク本文を含む）
  - `codex_output.txt` : Codex の標準出力/標準エラー
  - `codex_output_retry.txt` : 「no progress」の場合に自動再試行した出力
  - `codex_rc.txt` : Codex の終了コード
  - `verification.txt` : Verification に記載したコマンド実行ログ
  - `changed_paths.txt` : 差分として検出したパス（best effort）

---

## 2) よくあるエラーと原因

### A) `Task X no progress`（差分なし）
#### 典型原因
- Codex が「提案だけ」出してファイルを書いていない
- git worktree ではない環境で progress が検出できない

#### 対応
- `work/runs/task_XXX/codex_output*.txt` を見て、Codex が何を言っているか確認
- `git rev-parse --is-inside-work-tree` が通るか確認
- それでも無理な場合：`codex exec` の sandbox や実行モードが環境依存で合っていない可能性

---

### B) `must_change_globs not satisfied`
- タスクの `must_change_globs`（デフォルト `src/**`）に一致するファイルが変更されていない
- 例：docsだけ変更してしまった

---

### C) `NONCE missing` / `RESULT: DONE missing`
- Codex が task md の RESULT を更新していない
- Codex は **必ず** RESULT に NONCE と `RESULT: DONE` を書く必要がある

---

### D) `verification failed`
- `work/runs/task_XXX/verification.txt` を確認し、失敗したコマンドを直す
- Verification のコマンドは task md の `## Verification` セクションに記載する  
  - 推奨：```bash ... ``` の fenced block
  - もしくは `- `backticks`` 形式

---

## 3) 手動での自己診断チェック

### codex が動くか（stdin実行）
```bash
bash tools/codex_loop/selfcheck_codex_exec.sh
```

### git worktree か
```bash
git rev-parse --is-inside-work-tree
git status --porcelain
```

### platform import が通るか（editable install 前提）
```bash
python -c "import ml_platform"
python tools/platform_scan.py
```

---

## 4) それでも詰まる場合に貼ってほしい情報
以下を貼ると原因特定が速いです。

- 実行したコマンド（例：`python tools/codex_loop/run.py --repo . --once`）
- `work/runs/task_XXX/codex_output.txt` の末尾 50 行
- `work/runs/task_XXX/verification.txt`
- `git status --porcelain` の出力
