# S95_CODE_REVIEW: レビューしやすくする

## 観点
- 境界（core vs integrations vs registry）が守られているか
- ファイル増殖していないか（責務が明確か）
- HyperParameters 汚染が起きていないか
- 名前付けが “何をするファイルか” 分かるか
- 重要箇所（registry/clearml/ui contract）にコメントがあるか

## DoD
- PR差分が追いやすい
- 重要箇所が迷わず見つかる

