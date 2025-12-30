# codex_loop (tabular-analysis)

このフォルダは `work/queue.json` のタスクを順番に処理するための補助ツールです。

## 使い方
```bash
bash tools/codex_loop/selfcheck_codex_exec.sh
python tools/codex_loop/run.py --repo . --once
python tools/codex_loop/run.py --repo .
```

## DONE判定
- `work/tasks/Txxx_*.md` に `RESULT: DONE` が書かれたときのみ DONE とみなします。
- それ以外は **同じタスクを繰り返し**実行します（中途半端で次に進まない）。

