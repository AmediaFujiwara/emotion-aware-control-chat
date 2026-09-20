# Component Specifications（コンポーネント仕様）
<!-- spec-id: SPEC-CP -->

各モジュールの責務・インターフェース・エラーハンドリングを定義する。

---

## SPEC-CP-01：app.py（エントリーポイント）

**責務:** Streamlit UI の組み立て・セッション管理・処理フローの制御  
**種別:** UI / オーケストレーター

### セッション状態

| キー | 型 | 初期値 | 用途 |
|---|---|---|---|
| `messages` | `list[dict]` | `[]` | チャット表示用（role + content） |
| `turn_history` | `list[dict]` | `[]` | 分析履歴・エクスポート用 |
| `latest_analysis` | `AnxietyRiskVector \| None` | `None` | 最新チャートの描画元 |

### UI構成

**Sidebar:**
- Anthropic APIキー入力（`ANTHROPIC_API_KEY` 環境変数を初期値として読み込み）
- LLMモード切替トグル（APIキーがない場合は強制的に `False`）
- モデル名入力（デフォルト: `claude-sonnet-4-6`）
- スコア履歴リセットボタン（`st.rerun()` を呼ぶ）
- JSONエクスポートボタン（`turn_history` が1件以上の場合のみ表示）
- 医療免責事項表示

**Main:**
- タイトル + 3軸説明テーブル
- チャット履歴表示（`st.chat_message`）
- チャット入力（`st.chat_input`）
- 分析後: レーダーチャート + スコアパネル（1ターン以上）
- スコア推移グラフ（2ターン以上）

### 処理フロー（入力受信後）
1. ユーザーメッセージを即時表示・`messages` に追加
2. `analyze_user_input()` → `AnxietyRiskVector`
3. `generate_response()` → `str`
4. AI回答を表示・`messages` に追加
5. `build_turn_record()` → `turn_history` に追加
6. `latest_analysis` を更新
7. チャート類を描画

---

## SPEC-CP-02：schemas/anxiety_risk_vector.py

**責務:** データモデルの定義・バリデーション  
**種別:** データモデル層  
**詳細:** [data_models.md](data_models.md) 参照

---

## SPEC-CP-03：services/analyzer.py

**責務:** ユーザー入力テキストを `AnxietyRiskVector` に変換する  
**種別:** サービス層

### 公開インターフェース

```python
def analyze_user_input(
    user_text: str,                          # 最新ユーザーメッセージ
    conversation_context: list[dict[str, str]], # 直近の会話履歴
    use_llm: bool,                           # LLM使用フラグ
    api_key: str | None,                     # Anthropic APIキー
    model: str,                              # モデル名
) -> AnxietyRiskVector:
```

### 動作仕様

| 条件 | 動作 |
|---|---|
| `use_llm=False` または `api_key=None` | `fallback_rules.analyze_with_fallback()` を直接呼ぶ |
| `use_llm=True` かつ `api_key` あり | LLMClientを生成し `analyzer_prompt.md` をシステムプロンプトとして渡す |
| `ValidationError` 発生 | `analyze_with_fallback()` にフォールバック |
| その他の例外 | `analyze_with_fallback()` にフォールバック |

### プロンプト構成（LLMモード）
```
system: prompts/analyzer_prompt.md の全文
user:   【直近の会話履歴】（直近8メッセージ・各200文字で切り捨て）
        【ユーザーの最新入力】
```

### 出力保証
**常に有効な `AnxietyRiskVector` を返す**（例外を外部に伝播させない）

---

## SPEC-CP-04：services/responder.py

**責務:** `AnxietyRiskVector` に基づいて安定性優先の回答テキストを生成する  
**種別:** サービス層

### 公開インターフェース

```python
def generate_response(
    user_text: str,
    analysis: AnxietyRiskVector,
    conversation_context: list[dict[str, str]],
    use_llm: bool,
    api_key: str | None,
    model: str,
) -> str:
```

### 動作仕様

| 条件 | 動作 |
|---|---|
| `use_llm=False` または `api_key=None` | `_build_fallback_response(analysis)` でテンプレート回答を返す |
| `use_llm=True` かつ `api_key` あり | LLMに分析結果JSONを渡して回答を生成 |
| 例外発生 | テンプレート回答 + エラーメッセージを付記して返す |

### max_tokens 制御（SPEC-RP-08参照）

| 条件 | max_tokens |
|---|---|
| `analysis.is_high_load == True` | 600 |
| それ以外 | 1000 |

### プロンプト構成（LLMモード）
```
system: prompts/responder_prompt.md の全文
user:   【直近の会話履歴】（直近12メッセージ・各300文字で切り捨て）
        【ユーザーの最新入力】
        【分析結果 (AnxietyRiskVector)】（model_dump_json(indent=2)）
```

---

## SPEC-CP-05：services/llm_client.py

**責務:** Anthropic Messages API の薄いラッパー  
**種別:** インフラ層

### 公開インターフェース

```python
class LLMClient:
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"): ...

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> str: ...

    def chat_json(
        self,
        messages: list[dict[str, str]],
        system: str = "",
        temperature: float = 0.2,
        max_tokens: int = 2000,
    ) -> dict[str, Any]: ...
```

### エラーハンドリング

| 例外 | 変換後の LLMClientError メッセージ |
|---|---|
| `AuthenticationError` | "APIキーが無効です。..." |
| `RateLimitError` | "レート制限に達しました。..." |
| `APIConnectionError` | "Anthropic APIへの接続に失敗しました。..." |
| その他 | "LLM呼び出しエラー: {e}" |

### JSONパース（`chat_json`）
- レスポンスの先頭・末尾の ` ``` ` フェンスを自動除去してからパース
- `JSONDecodeError` は `LLMClientError` に変換

---

## SPEC-CP-06：components/radar_chart.py

**責務:** 3軸スコアをPlotlyレーダーチャートとして描画する  
**種別:** UIコンポーネント

### インターフェース

```python
def render_radar_chart(analysis: AnxietyRiskVector) -> None:
```

### 仕様

| 項目 | 値 |
|---|---|
| 軸ラベル | 境界侵害, 制御不能性, 予期的喪失 |
| スケール | 0〜10固定 |
| 塗りつぶし色 | `rgba(220, 80, 80, 0.25)` |
| 線色 | `rgba(220, 80, 80, 0.9)` |
| 高さ | 280px |

---

## SPEC-CP-07：components/score_panel.py

**責務:** スコア・方針・NI情報をパネル形式で表示する  
**種別:** UIコンポーネント

### インターフェース

```python
def render_score_panel(analysis: AnxietyRiskVector) -> None:
```

### 表示項目

| 項目 | 表示方法 |
|---|---|
| 各軸スコア（3つ） | `st.metric` + ASCIIバー |
| dominant_axis | テキスト |
| dominant_pattern | テキスト |
| should_use_ni | "⚠️ NI推奨" または "介入OK" |
| total_load | `/30` で表示 |
| primary_strategy | テキスト |
| minimal_action_today | テキスト |
| ni_reason（NI時のみ） | `st.info()` |
| safety_note（危機時のみ） | `st.error()` |

---

## SPEC-CP-08：components/history_chart.py

**責務:** 会話ターンを横軸とした3軸スコアの折れ線グラフを描画する  
**種別:** UIコンポーネント

### インターフェース

```python
def render_history_chart(turn_history: list[dict]) -> None:
```

### 仕様

| 項目 | 値 |
|---|---|
| X軸 | ターン番号（整数）|
| Y軸 | スコア（0〜10固定） |
| 系列色 | 境界侵害=#E05C5C / 制御不能性=#F0A030 / 予期的喪失=#5080E0 |
| データ0件時 | "スコア履歴がまだありません。" を表示して終了 |
| 高さ | 250px |

---

## SPEC-CP-09：utils/fallback_rules.py

**責務:** APIキー不要のキーワードベース分析を提供する  
**種別:** ユーティリティ層

### 公開インターフェース

```python
def analyze_with_fallback(user_text: str) -> AnxietyRiskVector:
```

### 処理ステップ
1. 各軸キーワードのマッチ数をカウント
2. `_score_from_count()` でスコア変換（0〜10）
3. 入力≥20文字かつ全スコア0 → ベースライン `bv=uc=al=2` を設定
4. `_detect_dominant_axis()` で最大スコア軸を選定
5. `_detect_dominant_pattern()` でパターン判定
6. `_build_response_policy()` で ResponsePolicy 構築
7. 危機ワード検出 → `safety_note` セット
8. 制御可能/不能因子・NI候補を生成
9. `AnxietyRiskVector` を組み立てて返す

---

## SPEC-CP-10：utils/storage.py

**責務:** セッション履歴のシリアライズ・エクスポート  
**種別:** ユーティリティ層

### 公開インターフェース

```python
def session_to_json(chat_history: list[dict[str, Any]]) -> str:
def build_turn_record(
    user_text: str,
    ai_response: str,
    analysis_dict: dict[str, Any],
) -> dict[str, Any]:
```

### エクスポートJSONの構造

```json
{
  "exported_at": "ISO8601",
  "app": "emotion-aware-control-chat",
  "version": "0.1.0",
  "turns": [
    {
      "timestamp": "ISO8601",
      "user_text": "...",
      "ai_response": "...",
      "analysis": { /* AnxietyRiskVector.model_dump() */ },
      "scores": {
        "boundary_violation": 0,
        "uncontrollability": 0,
        "anticipated_loss": 0
      }
    }
  ]
}
```
