# TASK 002: Hydra conf for usecase

## Context
- 非DSユーザーが dataset_id を入力し pipeline 実行できるように、用途固有のconfを用意する。

## Scope
- `conf/` を作成し、pipeline/preprocess/train/infer のtask root を用意
- ClearML project命名（例: MFG/<usecase>/...）を設定化
- `usecase_id` を設定に含める

## Acceptance Criteria
- [ ] conf が task単位に分割されている
- [ ] dataset_id が設定で指定できる
- [ ] project_name が用途別階層になっている

## Verification
```bash
python -m compileall -q .
find conf -type f | sort | head -200
```

## Completion Evidence (MUST include NONCE)
- NONCE:
- Files changed:
- Verification result:
- Notes:
