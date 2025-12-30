# S44 Risks & mitigations checklist

## 目的
`docs/09_RISKS_AND_MITIGATIONS.md` の事故を設計で先に潰す。

## チェックリスト（タスク完了前に必ず確認）
- [ ] A: 関連追跡（manifest / properties / pipeline_run.json）
- [ ] B: leaderboard対象の解決と保存（task_id保存）
- [ ] C: 比較可能性（split再生成禁止、bundle同梱、逆変換）
- [ ] D: UI汚染防止（hparams subset、plots最小、重い可視化はoptional）
- [ ] E: local/agent/clone 切替（doctor、set_script、queue確認）
- [ ] F: grid識別（grid_run_id tags、pipeline_run.json）
- [ ] G: 増殖防止（registry拡張、不要ファイル削除）

## DoD
- task md の `Risks addressed:` に該当項目が書かれている
- Evidence（Artifacts/Properties/Plots）で担保できている
