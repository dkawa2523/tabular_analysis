# ml-solution-template — Usecase Solution Repo (Polyrepo)

これは **用途別リポジトリ（Solution）のテンプレート**です。  
`ml-platform` を依存として使い、用途固有の差分（設定/registry/pipeline）だけ実装します。

## ユーザー導線（非DS）
1. ClearML上で `dataset_id` を入力して Pipeline を実行
2. `train_parent`（Training Summary）で **どのモデルが良いか**判断
3. 推奨モデル `model_id` を使って推論（single/batch/optimize）

## このSolutionが持つもの
- `conf/` : Hydra設定（用途固有のデフォルト/override）
- `src/usecase/` : pipeline定義・registry拡張・入口CLI
- `docs/` : Platform契約のスナップショット＋用途固有の運用手順
- `work/` : Codexタスク（用途固有に必要な実装）

## Local実行とClearML実行
- Local: `run.clearml.enabled=false` で核処理を実行（デバッグ/開発）
- ClearML Logging: `run.clearml.enabled=true`（Task/Artifacts/Plots）
- ClearML Agent: `enqueue=true` で `task.execute_remotely(queue=...)`
- ClearML UIから: `task.set_script(...)` により repository/entry_point を設定できる

---

## セットアップ
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements/base.txt
```

### Platform依存（開発時）
開発中は、Platformを editable install するのが簡単です:

```bash
pip install -e ../ml-platform
```

（本番では `ml-platform==X.Y.Z` にpin）

### ClearML初回設定
```bash
clearml-init
```

### Codex selfcheck / loop
```bash
bash tools/codex_loop/selfcheck_codex_exec.sh
python tools/codex_loop/run.py --repo . --once
python tools/codex_loop/run.py --repo .
```
