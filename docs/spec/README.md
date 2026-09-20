# Spec Documents — 仕様ドキュメント一覧

このディレクトリは Emotion-Aware Control Chat の **完全仕様書群** です。  
このドキュメント群があれば、プロジェクトをゼロから再現できます。

---

## ドキュメント一覧

| ファイル | SPEC-ID | 内容 | 変更頻度 |
|---|---|---|---|
| [system_overview.md](system_overview.md) | SPEC-SYS | 全体アーキテクチャ・コンポーネント図・技術スタック | 低 |
| [sequence_diagrams.md](sequence_diagrams.md) | SPEC-SQ | メインフロー・エラーフロー・エクスポートフローのMermaid図 | 低 |
| [data_models.md](data_models.md) | SPEC-DM | Pydanticモデル全フィールド・制約・スコアスケール | 中 |
| [axis_definitions.md](axis_definitions.md) | SPEC-AX | 3軸の定義・キーワード・スコアリングアルゴリズム | 中 |
| [response_policy_rules.md](response_policy_rules.md) | SPEC-RP | 8パターンの応答方針マッピング・NI条件 | **高** |
| [component_specs.md](component_specs.md) | SPEC-CP | 各モジュールの責務・インターフェース・エラーハンドリング | 中 |
| [traceability_matrix.md](traceability_matrix.md) | SPEC-TR | SPEC-ID → コードファイル対応表・変更提案テンプレート | **高** |

---

## 仕様変更の進め方

```
1. 変更したい内容を日本語で書く
   例: "制御不能優位のパターンで、NIを推奨するスコア閾値を7から6に下げたい"

2. traceability_matrix.md を開く
   → SPEC-RP-03 と SPEC-RP-10 が該当

3. traceability_matrix.md の「変更が必要なファイル」を確認
   → utils/fallback_rules.py:_build_response_policy()
   → prompts/analyzer_prompt.md

4. 該当する仕様ドキュメント（response_policy_rules.md）を先に変更
5. 変更提案テンプレートに沿ってコード変更箇所を提示
6. コードを変更し、traceability_matrix.md を更新
```

---

## SPEC-ID の命名規則

| プレフィックス | 対象 |
|---|---|
| `SPEC-SYS` | システム全体 |
| `SPEC-SQ` | シーケンス・フロー |
| `SPEC-DM` | データモデル |
| `SPEC-AX` | 3軸定義 |
| `SPEC-RP` | 応答方針ルール |
| `SPEC-CP` | コンポーネント |
| `SPEC-SF` | 安全機能 |
| `SPEC-TR` | トレーサビリティ自体 |

---

## 再現に必要な最小セット

このプロジェクトを別環境に移植・再実装する場合に必要な最小情報:

1. **[system_overview.md](system_overview.md)** — 何を作るか・技術スタック
2. **[data_models.md](data_models.md)** — データ構造
3. **[axis_definitions.md](axis_definitions.md)** — 3軸の意味とキーワード
4. **[response_policy_rules.md](response_policy_rules.md)** — AIの動作ルール
5. **[sequence_diagrams.md](sequence_diagrams.md)** — 処理の流れ
