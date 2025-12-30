# Task 002: registry: モデル/前処理/指標の拡張点を固定（LightGBM/Ridge/GPR + 標準前処理）

Status: done  
Priority: P0

## Goal
開発者が今後追加する場所を **registry に一本化**し、呼び出し側の改変を最小化する。

## Scope
### In scope
- `registry/models.py` に LightGBM/Ridge/GPR を登録（factoryで生成）
- `registry/metrics.py` に primary/others を扱える形で登録
- `registry/preprocessors.py` は将来拡張の入り口として固定（当面 core.preprocessing が組み立てる）
- conf/model や conf/preprocess の追加方針を docs に反映

### Out of scope
- preprocess/train の実処理実装（別タスク）

## Contracts (must follow)
- `docs/05_REGISTRY_EXTENSION.md`
- `AGENTS.md`

## Depends on
1

## Steps
1. registry の public API を確定（register/get の関数名を固定）
2. LightGBM が未インストールでも import error で落ちない設計にする（実行時に説明的に落とす）
3. モデル名の正規化（alias）は必要最低限に留める（増やしすぎない）
4. README/Docs に『追加する場所』を明記

## Acceptance Criteria
- [x] LightGBM/Ridge/GPR を `get_model(name, params)` で生成できる
- [x] 未知のモデル名は説明的な例外を出す
- [x] 拡張点が registry に集約されている

## Verification
- `python -c "from tabular_analysis.registry.models import get_model; print(type(get_model('ridge', {'alpha':1.0})))"`
- `python -c "from tabular_analysis.registry.metrics import get_metric; print(get_metric('rmse'))"`


## Platform reuse checklist (Codex MUST fill)
- Reused from ml-platform:
  - `ml_platform.registry` (PluginRegistry + register/get/list)
- Missing in ml-platform / implemented in solution:
  - None
- TODO candidates to move to platform:
  - None

## Risks addressed (Codex MUST fill; map to docs/09_RISKS_AND_MITIGATIONS.md)
- A (traceability): N/A
- B (leaderboard target selection): N/A
- C (comparability/leak/skew): N/A
- D (ClearML UI hygiene): N/A
- E (local/agent/clone): N/A
- F (grid explosion control): N/A
- G (bloat/cleanup): registry拡張点を固定しdocsに追記

## Notes / Risks
- ここで core.training はまだ実装しない。registry の入り口だけ固める。

## Next Improvements (Codex MUST write)
- train/preprocess の実装で registry の get_metrics/get_preprocessor を利用し、呼び出し側の分岐を増やさない
- conf/model と conf/preprocess の分割導入時は defaults 追加のみで統一する
- registry 拡張の最小例（custom metric）を docs/08 に追記

## RESULT
- NONCE: c4b964497857770f
- RESULT: DONE
- Completion Evidence: NONCE c4b964497857770f; registry modules updated + docs/05_REGISTRY_EXTENSION.md
- Verification:
  - `python -c "from tabular_analysis.registry.models import get_model; print(type(get_model('ridge', {'alpha':1.0})))"` -> `<class 'sklearn.linear_model._ridge.Ridge'>`
  - `python -c "from tabular_analysis.registry.metrics import get_metric; print(get_metric('rmse'))"` -> `<function rmse at 0x100f9fac0>`
- Files changed:
  - src/tabular_analysis/registry/models.py
  - src/tabular_analysis/registry/metrics.py
  - src/tabular_analysis/registry/preprocessors.py
  - docs/05_REGISTRY_EXTENSION.md
  - work/tasks/T002_registry.md
