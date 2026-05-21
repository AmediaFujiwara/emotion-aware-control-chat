"""
Keyword-based fallback analyzer for demo mode (no API key required).
Provides a rule-based AnxietyRiskVector when LLM is unavailable.
"""

from schemas.anxiety_risk_vector import AnxietyRiskVector, ResponsePolicy

# --- Keyword dictionaries ---

BOUNDARY_KEYWORDS = [
    "侵入", "境界", "責任", "役割", "どこまで", "押し付け", "巻き込まれ",
    "休めない", "説明しないといけない", "無限に", "曖昧な依頼", "全部自分",
    "私生活", "プライベート", "時間外", "仕事が入ってくる", "頼まれた",
    "やらされ", "断れない", "範囲", "限界", "過剰", "自分のことなのに",
    "自分の時間", "休息", "睡眠が取れない", "業務外", "勝手に",
]

UNCONTROLLABILITY_KEYWORDS = [
    "わからない", "相手次第", "判断次第", "制御できない", "どうなるか",
    "読めない", "変えられない", "終わらない", "納得しない", "会社の方針",
    "市場", "未来", "決まらない", "不確か", "振り回され", "誰が決める",
    "どうしたら", "どうすれば", "見通しがない", "予測できない", "相手が",
    "上司が", "組織が", "制度が", "どうなるかわからない", "どこに向かうか",
]

ANTICIPATED_LOSS_KEYWORDS = [
    "失う", "評価が下がる", "立場が悪くなる", "崩れる", "怖い", "将来",
    "生活", "健康", "家族", "取り返しがつかない", "不利になる",
    "失職", "クビ", "終わり", "壊れる", "失敗したら", "もし", "破綻",
    "信頼を失う", "大切なもの", "守れない", "なくなる", "消える",
    "いなくなる", "ダメになる", "挽回できない", "後悔", "手遅れ",
]

# Crisis keywords that trigger safety note
CRISIS_KEYWORDS = [
    "死にたい", "消えたい", "自傷", "自殺", "殺したい", "危害を加えたい",
    "もう無理", "今すぐ死ぬ", "死ぬしかない", "終わりにしたい",
    "自分を傷つけ", "消えてしまいたい",
]

SAFETY_MESSAGE = (
    "今すぐ一人で抱えないでください。"
    "緊急性がある場合は、地域の緊急窓口・医療機関・救急（119番）へ連絡してください。"
    "信頼できる人に今すぐ連絡することも選択肢の一つです。"
    "よりそいホットライン：0120-279-338（24時間）"
)


def _count_keywords(text: str, keywords: list[str]) -> int:
    """Count how many keywords appear in the text."""
    return sum(1 for kw in keywords if kw in text)


def _score_from_count(count: int, max_count: int = 5) -> int:
    """Convert keyword count to 0–10 score."""
    ratio = min(count / max_count, 1.0)
    return round(ratio * 10)


def _detect_dominant_axis(bv: int, uc: int, al: int) -> str:
    scores = {"Boundary Violation": bv, "Uncontrollability": uc, "Anticipated Loss": al}
    return max(scores, key=scores.get)


def _detect_dominant_pattern(bv: int, uc: int, al: int) -> str:
    threshold = 5

    high = []
    if bv >= threshold:
        high.append("BV")
    if uc >= threshold:
        high.append("UC")
    if al >= threshold:
        high.append("AL")

    if len(high) == 3:
        return "三軸高負荷"
    elif set(high) == {"BV", "UC"}:
        return "境界侵害 + 制御不能"
    elif set(high) == {"UC", "AL"}:
        return "制御不能 + 予期的喪失"
    elif set(high) == {"BV", "AL"}:
        return "境界侵害 + 予期的喪失"
    elif "BV" in high:
        return "境界侵害優位"
    elif "UC" in high:
        return "制御不能優位"
    elif "AL" in high:
        return "予期的喪失優位"
    else:
        return "低負荷 / 観察"


def _build_response_policy(bv: int, uc: int, al: int, pattern: str) -> ResponsePolicy:
    """Build response policy based on dominant pattern."""

    if pattern == "三軸高負荷":
        return ResponsePolicy(
            primary_strategy="介入を減らし安全と安定を確認する",
            secondary_strategy="解決策より負荷低減を優先する",
            avoid=["タスクを大量列挙する", "努力を促す", "長い分析をする", "行動を増やす"],
            recommended_response_style="短く、安定化優先、身体的回復を促す",
            should_use_ni=True,
            ni_reason="三軸すべて高負荷。解決策を増やすと負荷がさらに高まるため。",
        )
    elif pattern == "境界侵害 + 制御不能":
        return ResponsePolicy(
            primary_strategy="境界設定と論点の限定",
            secondary_strategy="制御不能な納得追求を止める",
            avoid=["全部引き受けさせる", "相手の内心を断定する", "未来予測を深掘りする"],
            recommended_response_style="範囲確認・確認文の提案・自分が抱える範囲の限定",
            should_use_ni=True,
            ni_reason="相手の完全な納得は制御不能。無限対応を止める必要がある。",
        )
    elif pattern == "制御不能 + 予期的喪失":
        return ResponsePolicy(
            primary_strategy="未来予測から距離を取り観測に留める",
            secondary_strategy="制御可能な今日の一点に縮小する",
            avoid=["長期予測を深掘りする", "判断材料がないことを扱う", "今すぐ結論を出させる"],
            recommended_response_style="今週・今日・次の一手への縮小",
            should_use_ni=True,
            ni_reason="会社方針・将来評価など制御不能な対象に向かっている。今は扱わない。",
        )
    elif pattern == "境界侵害 + 予期的喪失":
        return ResponsePolicy(
            primary_strategy="境界を守りながら失うかもしれないものを具体化する",
            secondary_strategy="未来の損失予測と現在の事実を分ける",
            avoid=["すぐ全部引き受けさせる", "根拠なく大丈夫と言う", "破局予測を拡大する"],
            recommended_response_style="今起きていること vs まだ起きていないことの分離",
            should_use_ni=False,
            ni_reason="",
        )
    elif pattern == "境界侵害優位":
        return ResponsePolicy(
            primary_strategy="役割・責任範囲・時間・作業範囲を明確化する",
            secondary_strategy="どこまで自分がやるべきかを整理する",
            avoid=["すぐ全部引き受けさせる", "追加作業を増やす", "相手の期待を過剰に読ませる"],
            recommended_response_style="対応より範囲確認を優先・確認文の例を出す",
            should_use_ni=False,
            ni_reason="",
        )
    elif pattern == "制御不能優位":
        return ResponsePolicy(
            primary_strategy="制御可能なものと制御不能なものを分ける",
            secondary_strategy="今やれる最小行動に縮小する",
            avoid=["相手の気持ちを断定する", "未来予測を深掘りする", "答えの出ない推測を続けさせる"],
            recommended_response_style="自分が扱えるもの / 扱えないものをリスト化・最小行動を1つに絞る",
            should_use_ni=uc >= 7,
            ni_reason="制御不能な対象を考え続けると不安が増幅するため。" if uc >= 7 else "",
        )
    elif pattern == "予期的喪失優位":
        return ResponsePolicy(
            primary_strategy="未来の損失予測と現在の事実を分ける",
            secondary_strategy="守るべきものを具体化し最悪ケースと回復可能性を分ける",
            avoid=["根拠なく大丈夫と言う", "未来不安を否定する", "破局予測をさらに拡大する"],
            recommended_response_style="今起きていること vs まだ起きていないことの分離・今日守るものに縮小",
            should_use_ni=al >= 8,
            ni_reason="まだ起きていない損失予測を今日扱うと不安が増幅するため。" if al >= 8 else "",
        )
    else:  # 低負荷
        return ResponsePolicy(
            primary_strategy="状況の整理と観察",
            secondary_strategy="自分の状態を確認する",
            avoid=["過剰な介入をする", "問題を大きく見せる"],
            recommended_response_style="穏やかな整理と観察",
            should_use_ni=False,
            ni_reason="",
        )


def _build_minimal_action(bv: int, uc: int, al: int, pattern: str) -> str:
    if pattern == "三軸高負荷":
        return "今日は水分を取り、横になる時間を10分でも確保する。大きな判断はしない。"
    elif "境界侵害" in pattern:
        return "今日対応する範囲を1つだけ決め、それ以外は明日に持ち越す。"
    elif "制御不能" in pattern:
        return "今日自分でできることを1つだけ書き出し、それだけを実行する。"
    elif "予期的喪失" in pattern:
        return "今日起きた事実だけを3行以内でメモし、まだ起きていないことは書かない。"
    else:
        return "今日の状態をそのまま観察し、無理に何かを解決しようとしない。"


def analyze_with_fallback(user_text: str) -> AnxietyRiskVector:
    """
    Keyword-based fallback analysis for demo mode.
    Returns an AnxietyRiskVector without calling any external API.
    """
    bv_count = _count_keywords(user_text, BOUNDARY_KEYWORDS)
    uc_count = _count_keywords(user_text, UNCONTROLLABILITY_KEYWORDS)
    al_count = _count_keywords(user_text, ANTICIPATED_LOSS_KEYWORDS)

    bv = _score_from_count(bv_count)
    uc = _score_from_count(uc_count)
    al = _score_from_count(al_count)

    # Ensure at least a minimal score if text has some emotional content
    has_emotional_content = len(user_text.strip()) > 20
    if has_emotional_content and bv == 0 and uc == 0 and al == 0:
        # Minimal baseline so chart renders meaningfully
        bv, uc, al = 2, 2, 2

    dominant_axis = _detect_dominant_axis(bv, uc, al)
    pattern = _detect_dominant_pattern(bv, uc, al)
    policy = _build_response_policy(bv, uc, al, pattern)

    # Safety note for crisis keywords
    safety_note = ""
    if any(kw in user_text for kw in CRISIS_KEYWORDS):
        safety_note = SAFETY_MESSAGE

    controllable = []
    uncontrollable = []
    ni_candidates = []

    if bv >= 5:
        controllable.append("自分が対応する範囲の限定")
        controllable.append("境界線の確認と伝達")
    if uc >= 5:
        uncontrollable.append("相手の判断・評価・感情")
        uncontrollable.append("組織・会社の方針")
        ni_candidates.append("相手の完全な納得を今日取りにいかない")
    if al >= 5:
        uncontrollable.append("将来の評価・立場の変化")
        ni_candidates.append("まだ起きていない損失予測を今日は扱わない")

    return AnxietyRiskVector(
        boundary_violation=bv,
        uncontrollability=uc,
        anticipated_loss=al,
        dominant_axis=dominant_axis,
        dominant_pattern=pattern,
        summary=f"[デモ分析] キーワード検出: 境界侵害={bv_count}語, 制御不能={uc_count}語, 予期的喪失={al_count}語",
        response_policy=policy,
        controllable_factors=controllable or ["現在の状態を観察すること"],
        uncontrollable_factors=uncontrollable or ["外部環境の変化"],
        non_intervention_candidates=ni_candidates,
        minimal_action_today=_build_minimal_action(bv, uc, al, pattern),
        stability_policy="今日は解決よりも安定を優先する。",
        safety_note=safety_note,
    )
