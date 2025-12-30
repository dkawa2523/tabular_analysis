# Task 014: ドキュメント仕上げ（非DS導線/開発者拡張/レビュー観点）

Status: todo  
Priority: P1

## Goal
完成時に、ユーザー/開発者/レビューアが迷わない docs を仕上げる。

## Scope
### In scope
- README の手順を実装完了状態に更新
- ClearML UIでどこを見るか（スクリーン構成）を明文化
- 拡張ポイント（registry/plots/config/clearml）の編集箇所を再確認

### Out of scope
- 長大な文章（必要最小限）

## Contracts (must follow)
- `docs/00_READING_ORDER.md`

## Depends on
10, 11

## Steps
1. docs の矛盾がないか確認し、最短導線を優先して改稿
2. レビュー観点（重要箇所）を docs に追記

## Acceptance Criteria
- [ ] 非DSが 'pipeline→leaderboard→infer' を迷わず辿れる記述がある
- [ ] 開発者がどこを触るか迷わない

## Verification
- `python -c "print('docs review')"`


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
- docs はコードより先に壊れやすい。最終確認を丁寧に。

## Next Improvements (Codex MUST write)
- (write suggestions for next tasks)

## RESULT
- NONCE: 
- RESULT: (TODO)  # Must be set to DONE to complete task
- Evidence (files/commands):
