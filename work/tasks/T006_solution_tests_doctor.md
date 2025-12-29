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
- NONCE:
- Files changed:
- Verification result:
- Notes:
