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
- NONCE: 53f9ac72b7954ba4b5f7745a444a3f78
- Files changed: src/usecase/registry_extensions.py, src/usecase/__init__.py, docs/15_CODEMAP.md, work/tasks/T005_solution_registry_extensions.md
- Verification result: python -m compileall -q . (pass); python -c "import usecase; print('ok')" (ok)
- Notes: Registered usecase-prefixed model/preprocessor/metric via platform registry helpers.
