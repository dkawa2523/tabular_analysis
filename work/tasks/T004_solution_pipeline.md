# TASK 004: Usecase pipeline definition

## Context
- ユーザーが ClearML で迷わない導線を実現するため、pipelineのstep定義を用途側で行う。

## Scope
- dataset->preprocess->train_parent を連結
- optionalで inference を追加できる
- step_task_ids.json をArtifactに残す

## Acceptance Criteria
- [ ] PipelineController で step が作成される設計
- [ ] step_task_ids.json が残る
- [ ] 入口CLIから実行できる

## Verification
```bash
python -m compileall -q .
python -m usecase.cli.pipeline --help || true
```

## Completion Evidence (MUST include NONCE)
- NONCE: c511efeec3c04c50b9909fe6ae537807
- Files changed: `conf/pipeline.yaml`, `src/usecase/cli/pipeline.py`, `work/tasks/T004_solution_pipeline.md`
- Verification result: `python -m compileall -q .` (pass), `python -m usecase.cli.pipeline --help || true` (pass)
- Notes: Defined ClearML PipelineController steps with dataset->preprocess->train_parent (+ optional infer) and step_task_ids artifact output.
