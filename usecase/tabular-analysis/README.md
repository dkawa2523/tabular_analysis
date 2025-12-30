# tabular-analysis (ml-solution usecase)

このフォルダは **ml-platform を利用する ml-solution のユースケース実装**です。  
目的は「非データサイエンスの製造開発エンジニア」が **ClearML 上で迷わず**、

1) データセットIDを入れて  
2) 前処理×モデルを複数評価して  
3) leaderboard で最良の組合せを選び  
4) 推論（single/batch/optimize）まで実行できる

状態を作ることです。

> 重要: **学習/前処理/推論は親子タスクにしません。**  
> 各タスクは ClearML 上で **独立したタスク**として実行・再実行でき、  
> 最後に `leaderboard` タスクが task_id 群を集約して比較します。

---

## 0. このユースケースが守る設計（要点）

- **polyrepo 前提**
  - `ml-platform` : 共通契約・共通I/O・ClearML連携ユーティリティ（壊さない）
  - `ml-solution-template` : ユースケース実装（tabular-analysis はここ）
- **独立タスク**
  - `dataset_register` / `preprocess` / `train` / `infer` / `leaderboard` はそれぞれ単体で動く
- **pipeline は「接着」**
  - pipeline は複数タスクを連続/並列に実行し、最後に leaderboard に task_id を渡すだけ
- **ClearML UI 契約**
  - HyperParameters = そのタスクの設定のみ
  - Properties/Artifacts/Plots/Debug Samples = 誤認しない配置（詳細は docs/03_CLEARML_UI_CONTRACT.md）

---

## 1. まずやること（Codex で実装を進める）

このフォルダには **codex-cli 用の指示ファイル群 (work/ と agentskills/ と tools/codex_loop)** が入っています。  
実装は Codex が `work/queue.json` のタスク順に行います。

### 1.1 展開場所
このZIPは workspace 直下で展開してください（例）:

```
<workspace>/
  ml-platform/               # 既に完成済み
  ml-solution-template/      # 既に完成済み
    usecase/tabular-analysis/  # ← このフォルダが追加される
```

### 1.2 venv & 依存
```bash
cd ml-solution-template/usecase/tabular-analysis
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements/base.txt

# tabular-analysis を editable install
pip install -e .

# 開発中は platform を editable install（推奨）
pip install -e ../../../ml-platform
```

### 1.3 ClearML 初回設定（必要な場合）
```bash
clearml-init
```

### 1.4 codex exec の自己診断（必須）
```bash
bash tools/codex_loop/selfcheck_codex_exec.sh
```

### 1.5 Codex ループ（まずは1回だけ）
```bash
python tools/codex_loop/run.py --repo . --once
```

問題がなければ継続:
```bash
python tools/codex_loop/run.py --repo .
```

---

## 2. 実装完了後の「ユーザー利用」最短導線（想定）

> ここは **最終的に** 実装完了後に動く導線です（Codex がコードを作り切る必要があります）。

### 2.1 ローカルで pipeline 実行（ClearML off でも可）
```bash
python -m tabular_analysis.cli.pipeline \
  run.mode=local \
  run.clearml.enabled=false \
  data.local_path=data/example.csv \
  data.target_col=target
```

### 2.2 ClearML on で pipeline 実行（ローカル実行しつつログを残す）
```bash
python -m tabular_analysis.cli.pipeline \
  run.mode=local \
  run.clearml.enabled=true \
  run.clearml.project_root="MFG/TabularAnalysis" \
  data.dataset_id="<CLEARML_DATASET_ID>" \
  data.target_col=target
```

### 2.3 ClearML Agent 実行（後で検証）
- `docs/07_PIPELINE_CONTRACT.md` と `docs/07_AGENT_EXECUTION.md` を参照
- テンプレートタスク clone 実行（repo URL / entry_point を config で指定できる設計）

---

## 3. どこを編集すれば拡張できるか（開発者向け）
- 前処理追加: `src/tabular_analysis/registry/preprocessors.py`
- モデル追加: `src/tabular_analysis/registry/models.py`
- 推論モード追加: `src/tabular_analysis/core/inference.py`
- 可視化追加: `src/tabular_analysis/core/plots.py`（task側で出す/出さないを制御）
- ClearML出力設計変更: `src/tabular_analysis/integrations/clearml/*`
- config 追加: `conf/` 以下（Hydra group）

---

## 4. ドキュメント
読む順番: `docs/00_READING_ORDER.md`



## 想定課題と対応策
- `docs/09_RISKS_AND_MITIGATIONS.md` を参照してください（Codexタスクにも組み込まれています）。

## ml-platform 雛形の再利用
- `docs/10_PLATFORM_TEMPLATE_USAGE.md` を参照してください。
- Codexは platform に既にあるユーティリティを優先して利用します（重複実装禁止）。


---

## Troubleshooting（詰まったとき）

- codex_loop のログ: `work/runs/task_XXX/`（prompt/codex_output/verification/changed_paths）
- 詳細: `docs/13_TROUBLESHOOTING.md`
