# S10 Architecture & polyrepo boundaries

## やること手順
1. **Platform vs Solution** の責務境界を守る
   - Platform: 契約・共通ライブラリ・ClearML/Hydra/Artifactsの型
   - Solution: 用途固有の設定・registry拡張・pipeline定義
2. SolutionにPlatformのロジックをコピペしない（依存で解決）
3. 重要入口（CLI/Pipeline）を `docs/15_CODEMAP.md` に反映
4. ファイルを増やす前に「同一ファイルで関数化」で済むか検討

## 事故りやすい点
- Solutionに共通処理を複製してドリフトが発生
- ClearML上でプロジェクト名/Propertiesが用途間で混ざる

## DoD
- 依存方向が保たれている
- CODEMAPが最新
- docs/00の不変条件に違反していない
