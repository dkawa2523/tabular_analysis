# TASK 007: Cleanup and docs finalize

## Context
- 運用目線のdocs（非DS導線）を完成させ、CODEMAPを最新にする。

## Scope
- docs/20,21 を実装に合わせて更新
- cleanup運用を追記
- READMEにmermaid/表を追加

## Acceptance Criteria
- [ ] READMEが導線を表とmermaidで説明
- [ ] CODEMAPが最新
- [ ] cleanup scriptが使える

## Verification
```bash
python -m compileall -q .
python tools/cleanup_repo.py --repo . --dry-run
```

## Completion Evidence (MUST include NONCE)
- NONCE:
- Files changed:
- Verification result:
- Notes:
