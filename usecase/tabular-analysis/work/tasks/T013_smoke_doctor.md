# Task 013: smoke/doctor: ローカルで end-to-end 検証（ClearML off→on）

Status: todo  
Priority: P1

## Goal
大規模実装でも壊れないよう、最小の自動検証（smoke/doctor）を用意する。

## Scope
### In scope
- 合成データ生成（小さな回帰）
- preprocess→train→leaderboard→infer(batch) をローカルで通す
- ClearML off を必須、on は optional（環境があれば）

### Out of scope
- 網羅的テスト（将来）

## Contracts (must follow)
- `AGENTS.md`

## Depends on
11

## Steps
1. `tools/smoke.py` を追加し、ワンコマンドで最小E2Eを通す
2. 失敗した場合の原因表示を丁寧にする

## Acceptance Criteria
- [ ] python tools/smoke.py が成功する（ClearML off）

## Verification
- `python -c "print('TODO: add tools/smoke.py and run it')"`


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
- これがあると Codex が途中で壊しても検出できる。

## Next Improvements (Codex MUST write)
- (write suggestions for next tasks)

## RESULT
- NONCE: 
- RESULT: (TODO)  # Must be set to DONE to complete task
- Evidence (files/commands):
