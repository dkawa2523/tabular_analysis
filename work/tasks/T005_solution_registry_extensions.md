# TASK 005: Usecase registry extensions (optional)

## Context
- Platformをforkせず、用途固有モデル/前処理を追加できることを示す。

## Scope
- usecase側 registry_extensions を用意し、platform registryへ登録する口を作る（薄く）

## Acceptance Criteria
- [ ] 追加登録の例がある
- [ ] Platform側との境界が守られている（コピペ禁止）

## Verification
```bash
python -m compileall -q .
python -c "import usecase; print('ok')"
```

## Completion Evidence (MUST include NONCE)
- NONCE:
- Files changed:
- Verification result:
- Notes:
