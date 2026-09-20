# Traceability Matrix（トレーサビリティマトリクス）
<!-- spec-id: SPEC-TR -->

## このドキュメントの使い方

**仕様変更を行う場合の手順:**

1. 変更内容に対応する SPEC-ID を左列から探す
2. 「変更が必要なファイル」列に列挙されたすべてのファイルを変更する
3. 本マトリクスの「最終更新」列を更新する

---

## マトリクス本体

| SPEC-ID | 仕様の内容 | 変更が必要なファイル | 連動する SPEC-ID |
|---|---|---|---|
| **SPEC-AX-01** | Boundary Violation の定義・スコア基準 | `utils/fallback_rules.py` → `BOUNDARY_KEYWORDS` リスト<br>`prompts/analyzer_prompt.md` → "Boundary Violation" セクション | SPEC-RP-02, SPEC-RP-05, SPEC-RP-07, SPEC-RP-08 |
| **SPEC-AX-02** | Uncontrollability の定義・スコア基準 | `utils/fallback_rules.py` → `UNCONTROLLABILITY_KEYWORDS` リスト<br>`prompts/analyzer_prompt.md` → "Uncontrollability" セクション | SPEC-RP-03, SPEC-RP-05, SPEC-RP-06, SPEC-RP-08, SPEC-RP-10 |
| **SPEC-AX-03** | Anticipated Loss の定義・スコア基準 | `utils/fallback_rules.py` → `ANTICIPATED_LOSS_KEYWORDS` リスト<br>`prompts/analyzer_prompt.md` → "Anticipated Loss" セクション | SPEC-RP-04, SPEC-RP-06, SPEC-RP-07, SPEC-RP-08, SPEC-RP-10 |
| **SPEC-AX-04** | フォールバックのスコア算出アルゴリズム | `utils/fallback_rules.py` → `_score_from_count()` | SPEC-DM-03 |
| **SPEC-DM-01** | ResponsePolicy モデルのフィールド追加・削除 | `schemas/anxiety_risk_vector.py` → `ResponsePolicy` クラス<br>`utils/fallback_rules.py` → `_build_response_policy()` 内の全 ResponsePolicy(...) 呼び出し<br>`prompts/analyzer_prompt.md` → "Output Schema" の response_policy 部分<br>`components/score_panel.py` → 表示項目 | SPEC-RP-* すべて |
| **SPEC-DM-02** | AnxietyRiskVector モデルのフィールド追加・削除 | `schemas/anxiety_risk_vector.py` → `AnxietyRiskVector` クラス<br>`utils/fallback_rules.py` → `analyze_with_fallback()` の return 文<br>`utils/storage.py` → `build_turn_record()`<br>`prompts/analyzer_prompt.md` → "Output Schema" 全体<br>`components/score_panel.py` → 表示項目<br>`components/history_chart.py` → scores キー参照 | SPEC-DM-01 |
| **SPEC-DM-03** | スコア閾値（≥5, ≥7, ≥8, ≥21）の変更 | `utils/fallback_rules.py` → `_detect_dominant_pattern()` の threshold<br>`utils/fallback_rules.py` → `_build_response_policy()` の UC≥7, AL≥8 条件<br>`schemas/anxiety_risk_vector.py` → `is_high_load` プロパティ | SPEC-RP-01, SPEC-RP-10 |
| **SPEC-RP-01** | dominant_pattern の種類・判定条件の変更 | `utils/fallback_rules.py` → `_detect_dominant_pattern()`<br>`prompts/analyzer_prompt.md` → "dominant_pattern の決定" セクション<br>`utils/fallback_rules.py` → `_build_response_policy()` の分岐<br>`utils/fallback_rules.py` → `_build_minimal_action()` の分岐 | SPEC-RP-02〜09 すべて |
| **SPEC-RP-02** | 境界侵害優位の応答方針変更 | `utils/fallback_rules.py` → `_build_response_policy()` の `elif pattern == "境界侵害優位"` ブロック<br>`prompts/analyzer_prompt.md` → "境界侵害優位の場合" セクション<br>`prompts/responder_prompt.md` → "境界侵害が高い場合" セクション | — |
| **SPEC-RP-03** | 制御不能優位の応答方針変更 | `utils/fallback_rules.py` → `_build_response_policy()` の `elif pattern == "制御不能優位"` ブロック<br>`prompts/analyzer_prompt.md` → "制御不能優位の場合" セクション<br>`prompts/responder_prompt.md` → "制御不能性が高い場合" セクション | SPEC-RP-10 |
| **SPEC-RP-04** | 予期的喪失優位の応答方針変更 | `utils/fallback_rules.py` → `_build_response_policy()` の `elif pattern == "予期的喪失優位"` ブロック<br>`prompts/analyzer_prompt.md` → "予期的喪失優位の場合" セクション<br>`prompts/responder_prompt.md` → "予期的喪失が高い場合" セクション | SPEC-RP-10 |
| **SPEC-RP-05** | 境界侵害+制御不能の応答方針変更 | `utils/fallback_rules.py` → `_build_response_policy()` の `elif pattern == "境界侵害 + 制御不能"` ブロック<br>`prompts/analyzer_prompt.md` → "境界侵害 + 制御不能の場合" セクション | — |
| **SPEC-RP-06** | 制御不能+予期的喪失の応答方針変更 | `utils/fallback_rules.py` → `_build_response_policy()` の `elif pattern == "制御不能 + 予期的喪失"` ブロック<br>`prompts/analyzer_prompt.md` → "制御不能 + 予期的喪失の場合" セクション | — |
| **SPEC-RP-07** | 境界侵害+予期的喪失の応答方針変更 | `utils/fallback_rules.py` → `_build_response_policy()` の `elif pattern == "境界侵害 + 予期的喪失"` ブロック | — |
| **SPEC-RP-08** | 三軸高負荷の応答方針・max_tokens変更 | `utils/fallback_rules.py` → `_build_response_policy()` の `if pattern == "三軸高負荷"` ブロック<br>`services/responder.py` → `max_tokens = 600 if analysis.is_high_load` の値<br>`prompts/analyzer_prompt.md` → "三軸高負荷の場合" セクション<br>`prompts/responder_prompt.md` → "三軸高負荷の場合" セクション | SPEC-DM-03 |
| **SPEC-RP-09** | 低負荷/観察の応答方針変更 | `utils/fallback_rules.py` → `_build_response_policy()` の `else` ブロック | — |
| **SPEC-RP-10** | NI推奨条件の変更 | `utils/fallback_rules.py` → `_build_response_policy()` の `should_use_ni` 設定箇所<br>`prompts/analyzer_prompt.md` → "NI（Non-Intervention）を使う条件" セクション<br>`prompts/responder_prompt.md` → "NI候補の提案" セクション | SPEC-RP-03, SPEC-RP-04 |
| **SPEC-SF-01** | 危機ワードリストの追加・削除 | `utils/fallback_rules.py` → `CRISIS_KEYWORDS` リスト | — |
| **SPEC-SF-02** | 安全メッセージ・ホットライン番号の変更 | `utils/fallback_rules.py` → `SAFETY_MESSAGE` 定数<br>`prompts/analyzer_prompt.md` → "safety_note の記載条件" セクション<br>`prompts/responder_prompt.md` → "危機的表現への対応" セクション<br>`docs/safety_note_jp.md` | — |
| **SPEC-CP-01** | UI構成・サイドバー項目の変更 | `app.py` 全体 | — |
| **SPEC-CP-03** | Analyzerの会話コンテキスト参照ターン数変更 | `services/analyzer.py` → `conversation_context[-8:]` の数値 | — |
| **SPEC-CP-04** | Responderの会話コンテキスト参照ターン数変更 | `services/responder.py` → `conversation_context[-12:]` の数値 | — |
| **SPEC-CP-05** | LLMプロバイダー変更（Anthropic → 他社） | `services/llm_client.py` 全体<br>`pyproject.toml` → dependencies<br>`app.py` → `ANTHROPIC_API_KEY` 環境変数名<br>`.env.example` | — |
| **SPEC-CP-06** | レーダーチャートの色・スケール変更 | `components/radar_chart.py` | — |
| **SPEC-CP-07** | スコアパネルの表示項目変更 | `components/score_panel.py` | SPEC-DM-02 |
| **SPEC-CP-08** | 時系列グラフの色・スケール変更 | `components/history_chart.py` | — |

---

## 変更提案テンプレート

仕様変更を提案する際は以下のフォーマットで記述してください。

```markdown
## 変更提案: [タイトル]

### 変更する仕様
- SPEC-ID: SPEC-XX-XX
- 変更前: [現在の仕様]
- 変更後: [変更後の仕様]

### 連動して変更が必要なファイル（traceability_matrix.mdより）
1. `path/to/file.py` — 変更箇所の説明
2. `prompts/xxx_prompt.md` — 変更箇所の説明

### 変更後の確認方法
- [ ] フォールバックモードで動作確認
- [ ] LLMモードで動作確認（APIキーがある場合）
```

---

## 更新ルール

- 新しい SPEC-ID を追加した場合、必ずこのマトリクスに行を追加する
- コードを変更してドキュメントと乖離した場合、**コードではなくドキュメントを正として修正する**
- このマトリクス自体の変更は `SPEC-TR` として扱う
