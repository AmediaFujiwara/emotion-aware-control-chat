# Sequence Diagrams
<!-- spec-id: SPEC-SQ -->

## SPEC-SQ-01：メインチャットフロー（LLMモード）

```mermaid
sequenceDiagram
    actor User
    participant UI as app.py (Streamlit)
    participant AZ as analyzer.py
    participant LLM as llm_client.py
    participant API as Anthropic API
    participant RS as responder.py
    participant ST as storage.py

    User->>UI: テキスト入力（st.chat_input）
    UI->>UI: st.session_state.messages に追加
    UI->>UI: ユーザーメッセージを即時表示

    UI->>AZ: analyze_user_input(user_text, context, use_llm=True, api_key, model)
    AZ->>LLM: LLMClient(api_key, model)
    AZ->>LLM: chat_json(messages, system=analyzer_prompt)
    LLM->>API: messages.create(model, system, messages)
    API-->>LLM: JSON文字列
    LLM-->>AZ: dict（パース済み）
    AZ->>AZ: AnxietyRiskVector.model_validate(dict)
    AZ-->>UI: AnxietyRiskVector

    UI->>RS: generate_response(user_text, analysis, context, use_llm=True, api_key, model)
    RS->>LLM: LLMClient(api_key, model)
    RS->>LLM: chat(messages, system=responder_prompt, temperature=0.4)
    LLM->>API: messages.create(model, system, messages)
    API-->>LLM: 回答テキスト
    LLM-->>RS: str
    RS-->>UI: str（AI回答）

    UI->>UI: AI回答を表示（st.chat_message）
    UI->>UI: st.session_state.messages に追加
    UI->>ST: build_turn_record(user_text, ai_response, analysis.model_dump())
    ST-->>UI: turn_record dict
    UI->>UI: session_state.turn_history に追加
    UI->>UI: render_radar_chart(analysis)
    UI->>UI: render_score_panel(analysis)
    UI->>UI: render_history_chart(turn_history)  ※2ターン以上の場合のみ
```

---

## SPEC-SQ-02：メインチャットフロー（デモモード / フォールバック）

```mermaid
sequenceDiagram
    actor User
    participant UI as app.py (Streamlit)
    participant AZ as analyzer.py
    participant FB as fallback_rules.py
    participant RS as responder.py

    User->>UI: テキスト入力
    UI->>AZ: analyze_user_input(user_text, context, use_llm=False, ...)
    AZ->>FB: analyze_with_fallback(user_text)
    FB->>FB: キーワードカウント（3軸）
    FB->>FB: スコア算出（_score_from_count）
    FB->>FB: パターン判定（_detect_dominant_pattern）
    FB->>FB: ResponsePolicy 構築（_build_response_policy）
    FB-->>AZ: AnxietyRiskVector
    AZ-->>UI: AnxietyRiskVector

    UI->>RS: generate_response(..., use_llm=False, ...)
    RS->>RS: _build_fallback_response(analysis)
    RS-->>UI: テンプレート回答文字列

    UI->>UI: 表示・保存・チャート描画
```

---

## SPEC-SQ-03：LLMエラー時のフォールバックフロー

```mermaid
sequenceDiagram
    participant AZ as analyzer.py
    participant LLM as llm_client.py
    participant API as Anthropic API
    participant FB as fallback_rules.py

    AZ->>LLM: chat_json(messages, system=prompt)
    LLM->>API: messages.create(...)
    API-->>LLM: エラー（AuthError / RateLimitError / ConnectionError）
    LLM-->>AZ: raise LLMClientError

    AZ->>AZ: except Exception → フォールバック
    AZ->>FB: analyze_with_fallback(user_text)
    FB-->>AZ: AnxietyRiskVector（キーワードベース）
    AZ-->>UI: AnxietyRiskVector（フォールバック結果）

    Note over AZ,FB: JSONパースエラー・Pydantic ValidationErrorでも同様に fallback
```

---

## SPEC-SQ-04：セッションエクスポートフロー

```mermaid
sequenceDiagram
    actor User
    participant UI as app.py（Sidebar）
    participant ST as storage.py

    User->>UI: 「セッションをJSONでエクスポート」ボタンクリック
    UI->>ST: session_to_json(turn_history)
    ST->>ST: JSON文字列に変換（exported_at, app, version, turns）
    ST-->>UI: JSON文字列
    UI-->>User: ファイルダウンロード（emotion_chat_YYYYMMDD_HHMMSS.json）
```

---

## SPEC-SQ-05：セッションリセットフロー

```mermaid
sequenceDiagram
    actor User
    participant UI as app.py（Sidebar）

    User->>UI: 「スコア履歴をリセット」ボタンクリック
    UI->>UI: session_state.messages = []
    UI->>UI: session_state.turn_history = []
    UI->>UI: session_state.latest_analysis = None
    UI->>UI: st.rerun()
```

---

## SPEC-SQ-06：危機ワード検出フロー

```mermaid
sequenceDiagram
    participant FB as fallback_rules.py
    participant RS as responder.py
    participant UI as app.py

    FB->>FB: CRISIS_KEYWORDS と user_text を照合
    alt 危機ワードあり
        FB->>FB: safety_note = SAFETY_MESSAGE（ホットライン等）
        FB-->>RS: AnxietyRiskVector（safety_note に値あり）
        RS->>RS: _build_fallback_response → safety_section を末尾に追加
        RS-->>UI: 回答テキスト（⚠️ 警告ブロック含む）
        UI->>UI: st.error() で赤背景表示（score_panel内）
    else 危機ワードなし
        FB-->>RS: AnxietyRiskVector（safety_note = ""）
    end
```
