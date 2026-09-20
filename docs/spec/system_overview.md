# System Overview
<!-- spec-id: SPEC-SYS -->

## 1. プロジェクト概要

**プロジェクト名:** Emotion-Aware Control Chat  
**バージョン:** 0.1.0  
**目的:** ユーザーの不安・悩みを3軸の構造的リスクベクトルとして分析し、AIの応答方針をその構造に応じて制御するチャットアプリ  
**実行環境:** ローカル（MacOS / Python 3.11+）  
**フレームワーク:** Streamlit  
**LLMプロバイダー:** Anthropic（claude-sonnet-4-6）  
**APIキー:** 環境変数 `ANTHROPIC_API_KEY` または Streamlit サイドバー入力

---

## 2. コンポーネント構成図

```
┌─────────────────────────────────────────────────────────────────┐
│  Streamlit UI  (app.py)                                         │
│                                                                 │
│  ┌──────────┐    ┌──────────────────────────────────────────┐  │
│  │ Sidebar  │    │ Main Area                                │  │
│  │ - APIキー │    │ - Chat UI (st.chat_message)              │  │
│  │ - モード  │    │ - RadarChart  (components/)              │  │
│  │ - モデル  │    │ - ScorePanel  (components/)              │  │
│  │ - リセット│    │ - HistoryChart(components/)              │  │
│  │ - エクスポ│    └──────────────────────────────────────────┘  │
│  └──────────┘                                                   │
└────────────────────┬────────────────────────────────────────────┘
                     │ calls
          ┌──────────┴──────────┐
          │                     │
   ┌──────▼──────┐      ┌───────▼──────┐
   │  Analyzer   │      │  Responder   │
   │ (services/) │      │ (services/)  │
   └──────┬──────┘      └───────┬──────┘
          │                     │
   ┌──────▼──────────────────────▼──────┐
   │         LLMClient (services/)      │
   │      Anthropic Messages API        │
   └──────────────────┬─────────────────┘
                      │ fallback on error
   ┌──────────────────▼─────────────────┐
   │      fallback_rules.py (utils/)    │
   │   キーワードベースルール分析        │
   └────────────────────────────────────┘
          │
   ┌──────▼──────────────────────────────┐
   │   AnxietyRiskVector (schemas/)      │
   │   Pydantic モデル（中間データ）      │
   └─────────────────────────────────────┘
```

---

## 3. ディレクトリ構成

```
emotion-aware-control-chat/
├── app.py                        # [SPEC-CP-01] Streamlit エントリーポイント
├── pyproject.toml                # 依存関係定義（uv）
├── .env / .env.example           # 環境変数
├── prompts/
│   ├── analyzer_prompt.md        # [SPEC-CP-03] Analyzerシステムプロンプト
│   └── responder_prompt.md       # [SPEC-CP-04] Responderシステムプロンプト
├── schemas/
│   └── anxiety_risk_vector.py    # [SPEC-DM-01][SPEC-DM-02] Pydanticモデル
├── services/
│   ├── llm_client.py             # [SPEC-CP-05] Anthropic APIラッパー
│   ├── analyzer.py               # [SPEC-CP-03] 分析サービス
│   └── responder.py              # [SPEC-CP-04] 回答生成サービス
├── components/
│   ├── radar_chart.py            # [SPEC-CP-06] レーダーチャート
│   ├── score_panel.py            # [SPEC-CP-07] スコアパネル
│   └── history_chart.py          # [SPEC-CP-08] 時系列グラフ
├── utils/
│   ├── fallback_rules.py         # [SPEC-CP-09] フォールバック分析
│   └── storage.py                # [SPEC-CP-10] セッション保存
└── docs/
    ├── spec/                     # ← 本ドキュメント群
    └── (既存ドキュメント)
```

---

## 4. 技術スタック

| レイヤー | 技術 | バージョン |
|---|---|---|
| UI | Streamlit | ≥1.35.0 |
| データモデル | Pydantic | ≥2.7.0 |
| LLMクライアント | Anthropic Python SDK | ≥0.40.0 |
| デフォルトモデル | claude-sonnet-4-6 | — |
| チャート | Plotly | ≥5.20.0 |
| データ操作 | pandas | ≥2.2.0 |
| 環境変数 | python-dotenv | ≥1.0.0 |
| パッケージ管理 | uv | — |
| Python | CPython | ≥3.11 |

---

## 5. 動作モード

| モード | 条件 | 分析 | 回答生成 |
|---|---|---|---|
| LLMモード | `ANTHROPIC_API_KEY` あり + トグルON | Anthropic API | Anthropic API |
| デモモード | APIキーなし または トグルOFF | キーワードルール | テンプレート |

LLMモードでAPIエラー・JSONパースエラーが発生した場合、自動的にデモモードにフォールバックする。

---

## 6. データフロー概要（詳細は sequence_diagrams.md 参照）

```
ユーザー入力
  → analyze_user_input()   → AnxietyRiskVector
  → generate_response()    → str（AI回答）
  → build_turn_record()    → session_state.turn_history
  → render_radar_chart()   → Plotlyチャート
  → render_score_panel()   → スコア・方針表示
  → render_history_chart() → 時系列グラフ（2ターン以上で表示）
```

---

## 7. 変更影響マトリクスの参照先

仕様変更時は [traceability_matrix.md](traceability_matrix.md) を最初に参照すること。  
SPEC-IDから変更が必要なファイルを特定できる。
