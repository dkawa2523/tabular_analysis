# CODEMAP（重要箇所）

## Entry points（CLI）
- Platform: `src/ml_platform/cli/*`
- Solution: `src/usecase/cli/pipeline.py`
- Solution: `src/usecase/cli/dataset_register.py`
- Solution: `src/usecase/cli/preprocess.py`
- Solution: `src/usecase/cli/train_model.py`
- Solution: `src/usecase/cli/train_parent.py`
- Solution: `src/usecase/cli/infer.py`（推論の親CLI）
- Solution: `src/usecase/cli/infer_single.py` / `infer_batch.py` / `infer_optimize.py`

## Workflows
- Platform: `src/ml_platform/workflow/*`（契約を守る接着層）
- Solution: `src/usecase/workflow/*`（用途固有の拡張）

## Registry extensions
- Solution: `src/usecase/registry_extensions.py`

## Integrations
- `src/ml_platform/integrations/clearml/*`

## Ops utilities
- `tools/cleanup_repo.py`（生成物の掃除）
