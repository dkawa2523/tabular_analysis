# TASK 003: ClearML execution modes wiring

## Context
- ローカル実行/Agent実行/UI clone 実行を両立させるため、set_scriptとenqueueを設計する。

## Scope
- `run.clearml.enabled` と `enqueue` と `script.repository/entry_point` を扱う
- UI clone 用に `task.set_script` を config で制御
- Agent mode: enqueue true なら execute_remotely を使う（タスク単体）

## Acceptance Criteria
- [ ] Local mode で動く
- [ ] ClearML logging mode で Task を作れる
- [ ] UI clone mode のための set_script 設定がある

## Verification
```bash
python -m compileall -q .
python -m usecase.cli.pipeline --help || true
```

## Completion Evidence (MUST include NONCE)
- NONCE:
- Files changed:
- Verification result:
- Notes:
