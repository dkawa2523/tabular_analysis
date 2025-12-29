# S50 ClearML datasets/versioning

## やること手順
1. dataset task は ClearML Dataset を作り `dataset_id` を発行
2. preprocess は lineage（src->dst）を必ず保存
3. schema/profile/debug_sample を標準Artifactとして残す
4. 大容量はDatasetへ、小容量はArtifactsへ
5. `usecase_id` を Properties/Tags に必ず付与（検索性）

## DoD
- dataset lineage が追える
- schemaが残る
- usecaseで混ざらない
