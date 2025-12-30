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
- NONCE: 53ea5de3ddb640a6a34b2c8ebfa5068d
- Files changed: README.md; docs/20_USECASE_GUIDE.md; docs/21_EXECUTION_MODES.md; docs/15_CODEMAP.md; tools/cleanup_repo.py; work/tasks/T007_solution_cleanup_docs.md
- Verification result: python -m compileall -q . (pass); python tools/cleanup_repo.py --repo . --dry-run (pass)
- Notes: Updated non-DS flow docs with table/mermaid, added cleanup guidance, and narrowed cleanup targets.
