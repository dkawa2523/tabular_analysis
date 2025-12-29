# CODEMAP（重要箇所）

## Entry points（CLI）
- Platform: `src/ml_platform/cli/*`
- Solution: `src/usecase/cli/*`（usecase側の入口）

## Workflows
- Platform: `src/ml_platform/workflow/*`（契約を守る接着層）
- Solution: `src/usecase/workflow/*`（用途固有の拡張）

## Integrations
- `src/ml_platform/integrations/clearml/*`
