# Response Policy Rules（応答方針マッピング）
<!-- spec-id: SPEC-RP -->

このドキュメントが「どのパターンでどの応答方針を取るか」の **Single Source of Truth** です。  
**このドキュメントを変更した場合、必ず traceability_matrix.md を参照し、対応するコード箇所を変更してください。**

---

## SPEC-RP-01：dominant_pattern の定義

スコアから判定される8種類のパターン。

| パターン名 | 判定条件 |
|---|---|
| `三軸高負荷` | BV≥5 AND UC≥5 AND AL≥5（全3軸が閾値以上） |
| `境界侵害 + 制御不能` | BV≥5 AND UC≥5（ALは問わない） |
| `制御不能 + 予期的喪失` | UC≥5 AND AL≥5（BVは問わない） |
| `境界侵害 + 予期的喪失` | BV≥5 AND AL≥5（UCは問わない） |
| `境界侵害優位` | BV≥5のみ |
| `制御不能優位` | UC≥5のみ |
| `予期的喪失優位` | AL≥5のみ |
| `低負荷 / 観察` | 全軸 < 5 |

**実装箇所:** `utils/fallback_rules.py:_detect_dominant_pattern`  
**LLMへの伝達:** `prompts/analyzer_prompt.md` の "dominant_pattern の決定" セクション

> 判定は優先順位順に評価される（三軸高負荷 → 複合2軸 → 単軸 → 低負荷）。

---

## SPEC-RP-02：境界侵害優位（`境界侵害優位`）

**適用条件:** BV≥5, UC<5, AL<5

| 項目 | 内容 |
|---|---|
| primary_strategy | "役割・責任範囲・時間・作業範囲を明確化する" |
| secondary_strategy | "どこまで自分がやるべきかを整理する" |
| avoid | "すぐ全部引き受けさせる" / "追加作業を増やす" / "相手の期待を過剰に読ませる" |
| recommended_response_style | "対応より範囲確認を優先・確認文の例を出す" |
| should_use_ni | `False` |
| ni_reason | `""` |

**minimal_action_today:** "今日対応する範囲を1つだけ決め、それ以外は明日に持ち越す。"

---

## SPEC-RP-03：制御不能優位（`制御不能優位`）

**適用条件:** UC≥5, BV<5, AL<5

| 項目 | 内容 |
|---|---|
| primary_strategy | "制御可能なものと制御不能なものを分ける" |
| secondary_strategy | "今やれる最小行動に縮小する" |
| avoid | "相手の気持ちを断定する" / "未来予測を深掘りする" / "答えの出ない推測を続けさせる" |
| recommended_response_style | "自分が扱えるもの / 扱えないものをリスト化・最小行動を1つに絞る" |
| should_use_ni | UC≥7 のとき `True`、それ以外 `False` |
| ni_reason | "制御不能な対象を考え続けると不安が増幅するため。"（UC≥7 の場合のみ） |

**minimal_action_today:** "今日自分でできることを1つだけ書き出し、それだけを実行する。"

---

## SPEC-RP-04：予期的喪失優位（`予期的喪失優位`）

**適用条件:** AL≥5, BV<5, UC<5

| 項目 | 内容 |
|---|---|
| primary_strategy | "未来の損失予測と現在の事実を分ける" |
| secondary_strategy | "守るべきものを具体化し最悪ケースと回復可能性を分ける" |
| avoid | "根拠なく大丈夫と言う" / "未来不安を否定する" / "破局予測をさらに拡大する" |
| recommended_response_style | "今起きていること vs まだ起きていないことの分離・今日守るものに縮小" |
| should_use_ni | AL≥8 のとき `True`、それ以外 `False` |
| ni_reason | "まだ起きていない損失予測を今日扱うと不安が増幅するため。"（AL≥8 の場合のみ） |

**minimal_action_today:** "今日起きた事実だけを3行以内でメモし、まだ起きていないことは書かない。"

---

## SPEC-RP-05：境界侵害 + 制御不能（`境界侵害 + 制御不能`）

**適用条件:** BV≥5 AND UC≥5, AL は問わない（三軸高負荷より低優先）

| 項目 | 内容 |
|---|---|
| primary_strategy | "境界設定と論点の限定" |
| secondary_strategy | "制御不能な納得追求を止める" |
| avoid | "全部引き受けさせる" / "相手の内心を断定する" / "未来予測を深掘りする" |
| recommended_response_style | "範囲確認・確認文の提案・自分が抱える範囲の限定" |
| should_use_ni | `True` |
| ni_reason | "相手の完全な納得は制御不能。無限対応を止める必要がある。" |

**minimal_action_today:** "今日対応する範囲を1つだけ決め、それ以外は明日に持ち越す。"

---

## SPEC-RP-06：制御不能 + 予期的喪失（`制御不能 + 予期的喪失`）

**適用条件:** UC≥5 AND AL≥5, BV は問わない

| 項目 | 内容 |
|---|---|
| primary_strategy | "未来予測から距離を取り観測に留める" |
| secondary_strategy | "制御可能な今日の一点に縮小する" |
| avoid | "長期予測を深掘りする" / "判断材料がないことを扱う" / "今すぐ結論を出させる" |
| recommended_response_style | "今週・今日・次の一手への縮小" |
| should_use_ni | `True` |
| ni_reason | "会社方針・将来評価など制御不能な対象に向かっている。今は扱わない。" |

**minimal_action_today:** "今日自分でできることを1つだけ書き出し、それだけを実行する。"

---

## SPEC-RP-07：境界侵害 + 予期的喪失（`境界侵害 + 予期的喪失`）

**適用条件:** BV≥5 AND AL≥5, UC は問わない

| 項目 | 内容 |
|---|---|
| primary_strategy | "境界を守りながら失うかもしれないものを具体化する" |
| secondary_strategy | "未来の損失予測と現在の事実を分ける" |
| avoid | "すぐ全部引き受けさせる" / "根拠なく大丈夫と言う" / "破局予測を拡大する" |
| recommended_response_style | "今起きていること vs まだ起きていないことの分離" |
| should_use_ni | `False` |
| ni_reason | `""` |

**minimal_action_today:** "今日対応する範囲を1つだけ決め、それ以外は明日に持ち越す。"

---

## SPEC-RP-08：三軸高負荷（`三軸高負荷`）

**適用条件:** BV≥5 AND UC≥5 AND AL≥5

| 項目 | 内容 |
|---|---|
| primary_strategy | "介入を減らし安全と安定を確認する" |
| secondary_strategy | "解決策より負荷低減を優先する" |
| avoid | "タスクを大量列挙する" / "努力を促す" / "長い分析をする" / "行動を増やす" |
| recommended_response_style | "短く、安定化優先、身体的回復を促す" |
| should_use_ni | `True` |
| ni_reason | "三軸すべて高負荷。解決策を増やすと負荷がさらに高まるため。" |

**minimal_action_today:** "今日は水分を取り、横になる時間を10分でも確保する。大きな判断はしない。"

**追加制約（Responder向け）:** `is_high_load=True` の場合、max_tokens を 600 に制限する。

---

## SPEC-RP-09：低負荷 / 観察（`低負荷 / 観察`）

**適用条件:** 全軸 < 5

| 項目 | 内容 |
|---|---|
| primary_strategy | "状況の整理と観察" |
| secondary_strategy | "自分の状態を確認する" |
| avoid | "過剰な介入をする" / "問題を大きく見せる" |
| recommended_response_style | "穏やかな整理と観察" |
| should_use_ni | `False` |
| ni_reason | `""` |

**minimal_action_today:** "今日の状態をそのまま観察し、無理に何かを解決しようとしない。"

---

## SPEC-RP-10：NI（Non-Intervention）推奨条件のまとめ

| 条件 | should_use_ni | 実装箇所 |
|---|---|---|
| パターンが「三軸高負荷」 | True | `fallback_rules.py:_build_response_policy` |
| パターンが「境界侵害 + 制御不能」 | True | 同上 |
| パターンが「制御不能 + 予期的喪失」 | True | 同上 |
| 制御不能優位 AND UC≥7 | True | 同上 |
| 予期的喪失優位 AND AL≥8 | True | 同上 |
| その他 | False | — |
