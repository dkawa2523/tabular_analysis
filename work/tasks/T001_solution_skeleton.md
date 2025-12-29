# TASK 001: Solution skeleton (usecase package + CLI stubs)

## Context
- Solution repoの入口。Platform依存を前提に、用途固有の最小骨組みを作る。

## Scope
- `src/usecase/` を作成
- `src/usecase/cli/` に stub を作成（pipeline, dataset_register, preprocess, train_parent, infer）
- Platform依存をREADME/pyprojectで示す

## Acceptance Criteria
- [ ] `python -c "import usecase"` が成功
- [ ] CLI stub が揃う
- [ ] docs/15 CODEMAP を更新

## Verification
```bash
python -m compileall -q .
python -c "import usecase"
ls -la src/usecase/cli
```

## Completion Evidence (MUST include NONCE)
- NONCE:
- Files changed:
- Verification result:
- Notes:
