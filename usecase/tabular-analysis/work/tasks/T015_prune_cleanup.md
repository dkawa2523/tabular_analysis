# Task 015: 不要コード・不要ファイル削除（tabular-analysis内のprune task）

Status: todo  
Priority: P1

## Goal
開発の途中で増えた不要ファイル/死コードを削除し、構成が膨大化しないようにする。

## Scope
### In scope
- 未使用ファイルを削除（vulture などの静的検出 + 手確認）
- docs と実装が乖離している部分を修正
- 重複ユーティリティを統合（platform側へ寄せるかsolution内で統一）

### Out of scope
- 大規模なAPI破壊（必要なら新タスク化）

## Contracts (must follow)
- `AGENTS.md`

## Depends on
14

## Steps
1. 不要ファイル候補を列挙し、削除前にどこから参照されているか確認
2. 削除後に smoke を通す
3. work/queue.json の完了条件を満たすまで繰り返す

## Acceptance Criteria
- [ ] smoke が通る
- [ ] 不要ファイルが残っていない

## Verification
- `python tools/smoke.py`


## Platform reuse checklist (Codex MUST fill)
- Reused from ml-platform:
  - 
- Missing in ml-platform / implemented in solution:
  - 
- TODO candidates to move to platform:
  - 

## Risks addressed (Codex MUST fill; map to docs/09_RISKS_AND_MITIGATIONS.md)
- A (traceability):
- B (leaderboard target selection):
- C (comparability/leak/skew):
- D (ClearML UI hygiene):
- E (local/agent/clone):
- F (grid explosion control):
- G (bloat/cleanup):

## Notes / Risks
- prune は最後に必ずやる（将来の負債を減らす）。

## Next Improvements (Codex MUST write)
- (write suggestions for next tasks)

## RESULT
- NONCE: 
- RESULT: (TODO)  # Must be set to DONE to complete task
- Evidence (files/commands):
