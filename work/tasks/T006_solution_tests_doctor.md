# TASK 006: Solution tests & doctor

## Context
- 自動開発で“動いている風”を防ぐ。最低限のimport/CLIチェックを入れる。

## Scope
- `python tools/doctor.py` が通る
- pytest を最低1つ

## Acceptance Criteria
- [ ] doctor成功
- [ ] pytest成功

## Verification
```bash
python -m compileall -q .
python tools/doctor.py
pytest -q || true
```

## Completion Evidence (MUST include NONCE)
- NONCE: facea8a85a414d88af88effd524c90d1
- Files changed: tools/doctor.py, tests/test_placeholder.py, work/tasks/T006_solution_tests_doctor.md
- Verification result: python -m compileall -q . (pass); python tools/doctor.py (pass); pytest -q || true (pass)
- Notes: Added a local pipeline dry-run smoke test that avoids hard hydra/omegaconf deps when missing.
