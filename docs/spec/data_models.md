# Data Models
<!-- spec-id: SPEC-DM -->

**実装ファイル:** `schemas/anxiety_risk_vector.py`

---

## SPEC-DM-01：ResponsePolicy

AIの応答戦略を定義するモデル。AnxietyRiskVector の内部に埋め込まれる。

```python
class ResponsePolicy(BaseModel):
    primary_strategy: str          # 主方針（例: "制御可能と不能を分ける"）
    secondary_strategy: str        # 副方針
    avoid: list[str]               # 禁止事項リスト（AIに渡され回答から除外される）
    recommended_response_style: str # 推奨回答スタイルの説明
    should_use_ni: bool            # NI（非介入）を使うか
    ni_reason: str                 # NIを使う理由（should_use_ni=True の場合のみ意味を持つ）
```

### フィールド制約

| フィールド | 型 | デフォルト | 制約 |
|---|---|---|---|
| primary_strategy | str | 必須 | — |
| secondary_strategy | str | 必須 | — |
| avoid | list[str] | `[]` | 0件以上 |
| recommended_response_style | str | 必須 | — |
| should_use_ni | bool | `False` | — |
| ni_reason | str | `""` | should_use_ni=False のとき空文字 |

### 変更影響
このモデルを変更する場合 → [SPEC-RP-*] の全パターン定義も連動して変更が必要。

---

## SPEC-DM-02：AnxietyRiskVector

3軸スコアと回答方針を統合した中間データ構造。  
Analyzerが生成し、Responderが消費する。

```python
class AnxietyRiskVector(BaseModel):
    # 3軸スコア（0〜10）
    boundary_violation: int         # 境界侵害スコア
    uncontrollability: int          # 制御不能性スコア
    anticipated_loss: int           # 予期的喪失スコア

    # 派生メタデータ
    dominant_axis: str              # 最も強い軸名（英語）
    dominant_pattern: str           # 支配的パターン（8種類 → SPEC-RP-01参照）
    summary: str                    # 不安構造の要約文（日本語）

    # 応答方針
    response_policy: ResponsePolicy # SPEC-DM-01 参照

    # 要因リスト
    controllable_factors: list[str]        # 制御可能な要素
    uncontrollable_factors: list[str]      # 制御不能な要素
    non_intervention_candidates: list[str] # NI候補リスト

    # 行動ガイダンス
    minimal_action_today: str       # 今日の最小行動（1文）
    stability_policy: str           # 安定性方針（1文）
    safety_note: str                # 危機時の安全注意（通常は空文字）
```

### フィールド制約

| フィールド | 型 | デフォルト | 制約 |
|---|---|---|---|
| boundary_violation | int | 必須 | 0〜10（バリデーターでクランプ） |
| uncontrollability | int | 必須 | 0〜10（バリデーターでクランプ） |
| anticipated_loss | int | 必須 | 0〜10（バリデーターでクランプ） |
| dominant_axis | str | 必須 | "Boundary Violation" / "Uncontrollability" / "Anticipated Loss" のいずれか |
| dominant_pattern | str | 必須 | SPEC-RP-01 の8種類のいずれか |
| summary | str | 必須 | — |
| response_policy | ResponsePolicy | 必須 | ネストオブジェクト |
| controllable_factors | list[str] | `[]` | — |
| uncontrollable_factors | list[str] | `[]` | — |
| non_intervention_candidates | list[str] | `[]` | — |
| minimal_action_today | str | 必須 | 1文推奨 |
| stability_policy | str | 必須 | 1文推奨 |
| safety_note | str | `""` | SPEC-SF-01 参照 |

### 計算プロパティ

| プロパティ | 算出式 | 用途 |
|---|---|---|
| `total_load` | `bv + uc + al` | 全体負荷量（0〜30） |
| `is_high_load` | `(bv≥7 AND uc≥7 AND al≥7) OR total_load≥21` | 三軸高負荷フラグ。Responderのmax_tokens制御に使用 |

### セッション保存時のフォーマット（SPEC-CP-10参照）

```json
{
  "timestamp": "2026-09-21T10:30:00",
  "user_text": "...",
  "ai_response": "...",
  "analysis": { /* AnxietyRiskVector.model_dump() */ },
  "scores": {
    "boundary_violation": 7,
    "uncontrollability": 5,
    "anticipated_loss": 3
  }
}
```

---

## SPEC-DM-03：スコアスケールの定義

LLMおよびフォールバックルールが使用するスコア基準。

| スコア | 意味 | 該当状態 |
|---|---|---|
| 0〜2 | ほとんど見られない | 低負荷 |
| 3〜4 | 軽度 | 観察レベル |
| 5〜6 | 中程度 | 対応要 |
| 7〜8 | 強い | 高負荷 |
| 9〜10 | 非常に強い | 最高負荷 |

**閾値の使用箇所:**

| 閾値 | 用途 | 実装箇所 |
|---|---|---|
| ≥5 | dominant_pattern 判定（高い軸の判定） | `fallback_rules.py:_detect_dominant_pattern` |
| ≥7 | UC優位でNI推奨 | `fallback_rules.py:_build_response_policy` |
| ≥7（全軸）または合計≥21 | 三軸高負荷判定 | `anxiety_risk_vector.py:is_high_load` |
| ≥8 | AL優位でNI推奨 | `fallback_rules.py:_build_response_policy` |

### 変更影響
スコア閾値を変更する場合 → `SPEC-DM-03` の表を更新 → `fallback_rules.py` の該当箇所 + `anxiety_risk_vector.py:is_high_load` を変更。
