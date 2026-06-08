from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List


@dataclass
class CommercialValidationResult:
    commercial_promise: float
    creative_potential: float
    binge_potential: float
    test50_value: float
    investment_attractiveness: float
    recommendation: str
    evidence: Dict[str, Any]


def clamp_score(value: float) -> float:
    return round(max(0.0, min(10.0, value)), 2)


def compact_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def split_sentences(text: str) -> List[str]:
    text = compact_text(text)
    if not text:
        return []
    return [x.strip() for x in re.split(r"[。！？!?；;]\s*", text) if x.strip()]


def count_question_pressure(sentences: Iterable[str]) -> int:
    count = 0
    for s in sentences:
        if "？" in s or "?" in s:
            count += 1
        if any(x in s for x in ["为什么", "怎么", "是谁", "到底", "真相", "秘密"]):
            count += 1
    return count


def count_conflict_pressure(sentences: Iterable[str]) -> int:
    count = 0
    for s in sentences:
        if any(x in s for x in ["逼", "辱", "恨", "杀", "抢", "骗", "跪", "赶", "夺", "威胁", "背叛", "离婚", "报仇"]):
            count += 1
    return count


def count_turning_points(sentences: Iterable[str]) -> int:
    count = 0
    for s in sentences:
        if any(x in s for x in ["突然", "没想到", "谁知", "原来", "竟然", "反而", "转身", "终于", "下一刻"]):
            count += 1
    return count


def count_creative_hooks(sentences: Iterable[str]) -> int:
    hooks = 0
    for s in sentences:
        if len(s) < 8:
            continue
        has_shock = any(x in s for x in ["背叛", "羞辱", "抛弃", "离婚", "秘密", "真相", "身份", "复仇", "逆袭", "跪求", "首富", "权势"])
        has_action = any(x in s for x in ["发现", "揭穿", "回归", "逃离", "反击", "夺回", "失去", "得到", "宣布", "拒绝"])
        if has_shock and has_action:
            hooks += 1
    return hooks


def score_from_count(count: int, low: int, high: int) -> float:
    if count <= low:
        return 3.0 + count
    if count >= high:
        return 9.0
    return 4.0 + (count - low) * (5.0 / max(1, high - low))


def build_hook_analysis(text: str) -> Dict[str, Any]:
    """
    Detect reusable commercial hooks from sampled source text.

    V0.2 principle:
    - This is still rule-based.
    - Hook labels are market-facing and reusable.
    - Source-language trigger words are kept as unicode escapes to avoid encoding issues.
    """

    hook_rules = {
        "rebirth": [
            "\u91cd\u751f", "\u56de\u5230", "\u518d\u6765\u4e00\u6b21",
        ],
        "revenge_counterattack": [
            "\u590d\u4ec7", "\u62a5\u4ec7", "\u53cd\u51fb", "\u7ffb\u8eab", "\u8ba8\u56de",
        ],
        "family_conflict": [
            "\u7239", "\u5a18", "\u5bb6\u91cc", "\u5bb6\u4eba", "\u59b9", "\u59d0", "\u5ac1", "\u5eb6\u59b9", "\u5ae1\u5eb6",
        ],
        "humiliation_face_slap": [
            "\u7f9e\u8fb1", "\u8fb1", "\u8dea", "\u4e0d\u914d", "\u6253\u4f60", "\u6253\u8138",
        ],
        "marriage_divorce": [
            "\u548c\u79bb", "\u79bb\u5a5a", "\u4eb2\u4e8b", "\u5ac1\u7ed9", "\u6210\u4eb2",
        ],
        "survival_threat": [
            "\u6740", "\u6b7b", "\u5bb3\u6b7b", "\u9003", "\u6d3b\u4e0b\u53bb",
        ],
        "status_identity": [
            "\u8eab\u4efd", "\u5ae1\u5973", "\u5eb6\u5973", "\u9996\u5bcc", "\u6743\u52bf", "\u5bb6\u4e1a",
        ],
        "healing_business_skill": [
            "\u836f", "\u533b", "\u795e\u533b", "\u963f\u80f6", "\u751f\u610f", "\u8d5a\u94b1",
        ],
    }

    detected_hooks: List[str] = []
    hook_counts: Dict[str, int] = {}

    for hook, terms in hook_rules.items():
        count = 0
        for term in terms:
            count += text.count(term)
        hook_counts[hook] = count
        if count > 0:
            detected_hooks.append(hook)

    marketing_angles: List[Dict[str, str]] = []

    angle_templates = {
        "rebirth": {
            "angle": "Rebirth second-chance hook",
            "why_it_matters": "A second-chance opening can create immediate curiosity and strong read-next pressure.",
        },
        "revenge_counterattack": {
            "angle": "Revenge and counterattack arc",
            "why_it_matters": "Revenge arcs are easy to turn into short-form ad hooks and cliffhanger copy.",
        },
        "family_conflict": {
            "angle": "Family oppression and emotional conflict",
            "why_it_matters": "Family conflict is emotionally legible and can support strong Facebook/TikTok creatives.",
        },
        "humiliation_face_slap": {
            "angle": "Humiliation-to-face-slap payoff",
            "why_it_matters": "Humiliation followed by payoff is a reusable ad structure for serialized fiction.",
        },
        "marriage_divorce": {
            "angle": "Marriage or separation pressure",
            "why_it_matters": "Relationship stakes help simplify the story into clear ad copy.",
        },
        "survival_threat": {
            "angle": "Life-or-death pressure",
            "why_it_matters": "Survival pressure raises urgency and helps build cliffhanger-driven creatives.",
        },
        "status_identity": {
            "angle": "Status and identity reversal",
            "why_it_matters": "Identity/status shifts are useful for secret-reveal and comeback creatives.",
        },
        "healing_business_skill": {
            "angle": "Special skill or business-growth hook",
            "why_it_matters": "A visible skill path can support long-term growth, SEO themes, and episodic promotion.",
        },
    }

    for hook in detected_hooks:
        if hook in angle_templates:
            marketing_angles.append(angle_templates[hook])

    creative_signal_count = sum(1 for hook in detected_hooks if hook_counts.get(hook, 0) > 0)
    creative_signal_count += min(20, sum(min(v, 3) for v in hook_counts.values()))

    return {
        "detected_hooks": detected_hooks,
        "hook_counts": hook_counts,
        "creative_signal_count": creative_signal_count,
        "marketing_angles": marketing_angles,
    }


def build_validation_explanation(
    *,
    commercial_promise: float,
    creative_potential: float,
    binge_potential: float,
    test50_value: float,
    investment_attractiveness: float,
    recommendation: str,
    evidence: Dict[str, Any],
) -> Dict[str, Any]:
    reasons: List[str] = []
    risks: List[str] = []
    suggested_next_action = recommendation

    question_pressure = int(evidence.get("question_pressure", 0) or 0)
    conflict_pressure = int(evidence.get("conflict_pressure", 0) or 0)
    turning_points = int(evidence.get("turning_points", 0) or 0)
    creative_hooks = int(evidence.get("creative_hooks", 0) or 0)
    creative_signal_count = int(evidence.get("creative_signal_count", creative_hooks) or 0)
    detected_hooks = list(evidence.get("detected_hooks", []) or [])
    marketing_angles = list(evidence.get("marketing_angles", []) or [])
    chapter_count = int(evidence.get("chapter_count", 0) or 0)

    if commercial_promise >= 8:
        reasons.append("Opening and sampled chapters show strong commercial promise through unresolved pressure and conflict.")
    elif commercial_promise >= 6:
        reasons.append("Commercial promise is present but not yet clearly explosive.")
    else:
        risks.append("Commercial promise is weak; sampled chapters may not create enough must-continue-reading pressure.")

    if creative_potential >= 8:
        reasons.append("Sampled chapters contain many potentially reusable ad angles.")
    elif creative_potential >= 5:
        reasons.append("Some ad angles exist, but creative density needs stronger extraction.")
    else:
        risks.append("Creative potential is currently weak; few clear ad hooks were detected by V0 rules.")

    if detected_hooks:
        reasons.append("Detected reusable commercial hooks: " + ", ".join(detected_hooks[:8]) + ".")
    else:
        risks.append("No strong reusable commercial hook category was detected.")

    if binge_potential >= 8:
        reasons.append("Conflict and turning-point density suggest good binge-reading potential.")
    elif binge_potential >= 6:
        reasons.append("There is some continuation drive, but long-form stickiness still needs validation.")
    else:
        risks.append("Binge potential is weak; middle and later sampled sections may not sustain momentum.")

    if test50_value >= 7:
        reasons.append("The book is suitable for a 50-chapter market test before full investment.")
    else:
        risks.append("The book may not be strong enough for a 50-chapter validation round.")

    if chapter_count < 20:
        risks.append("Sample size is small; validation confidence is limited.")

    if recommendation == "HIGH_PRIORITY":
        suggested_next_action = "Prioritize this book for 50-chapter production and growth testing."
    elif recommendation == "TEST_50_CHAPTERS":
        suggested_next_action = "Produce and test the first 50 adapted chapters before committing to full-book production."
    elif recommendation == "LOW_PRIORITY_TEST":
        suggested_next_action = "Only test if production capacity is available; otherwise keep in reserve."
    else:
        suggested_next_action = "Skip for now unless later market evidence changes."

    return {
        "summary": {
            "recommendation": recommendation,
            "suggested_next_action": suggested_next_action,
        },
        "reasons": reasons,
        "risks": risks,
        "evidence_samples": {
            "question_pressure": question_pressure,
            "conflict_pressure": conflict_pressure,
            "turning_points": turning_points,
            "creative_hooks": creative_hooks,
            "creative_signal_count": creative_signal_count,
            "detected_hooks": detected_hooks,
            "marketing_angles": marketing_angles,
            "chapter_count": chapter_count,
        },
    }


def validate_commercial_value(
    chapters: List[str],
    *,
    book_id: str = "",
) -> Dict[str, Any]:
    """
    Growth-system commercial validation.

    Scope:
    - Evaluate investment potential from selected Chinese source chapters.
    - Do not generate Story Bible.
    - Do not rewrite or translate.
    - Do not depend on Reader/Reviewer documents.

    Input:
    - chapters: sampled Chinese chapter texts.

    Output:
    - dict suitable for JSON serialization.
    """

    normalized = [compact_text(x) for x in chapters if compact_text(x)]
    all_text = "\n".join(normalized)
    sentences = split_sentences(all_text)

    chapter_count = len(normalized)
    total_chars = len(all_text)

    question_pressure = count_question_pressure(sentences)
    conflict_pressure = count_conflict_pressure(sentences)
    turning_points = count_turning_points(sentences)
    creative_hooks = count_creative_hooks(sentences)
    hook_analysis = build_hook_analysis(all_text)
    creative_signal_count = max(
        creative_hooks,
        int(hook_analysis.get("creative_signal_count", 0) or 0),
    )

    commercial_promise = clamp_score(
        score_from_count(question_pressure + conflict_pressure, low=5, high=35)
    )

    creative_potential = clamp_score(
        score_from_count(creative_signal_count, low=2, high=18)
    )

    binge_potential = clamp_score(
        score_from_count(turning_points + conflict_pressure, low=8, high=45)
    )

    test50_value = clamp_score(
        commercial_promise * 0.35
        + creative_potential * 0.25
        + binge_potential * 0.30
        + (1.0 if chapter_count >= 10 else 0.3)
    )

    investment_attractiveness = clamp_score(
        commercial_promise * 0.35
        + creative_potential * 0.30
        + binge_potential * 0.20
        + test50_value * 0.15
    )

    if investment_attractiveness >= 8.0:
        recommendation = "HIGH_PRIORITY"
    elif investment_attractiveness >= 6.5:
        recommendation = "TEST_50_CHAPTERS"
    elif investment_attractiveness >= 5.0:
        recommendation = "LOW_PRIORITY_TEST"
    else:
        recommendation = "SKIP"

    evidence = {
        "book_id": book_id,
        "chapter_count": chapter_count,
        "total_chars": total_chars,
        "sentence_count": len(sentences),
        "question_pressure": question_pressure,
        "conflict_pressure": conflict_pressure,
        "turning_points": turning_points,
        "creative_hooks": creative_hooks,
        "creative_signal_count": creative_signal_count,
        "detected_hooks": hook_analysis.get("detected_hooks", []),
        "hook_counts": hook_analysis.get("hook_counts", {}),
        "marketing_angles": hook_analysis.get("marketing_angles", []),
        "note": "Rule-based first version. No Story Bible, no Reader/Reviewer, no rewrite.",
    }

    result = CommercialValidationResult(
        commercial_promise=commercial_promise,
        creative_potential=creative_potential,
        binge_potential=binge_potential,
        test50_value=test50_value,
        investment_attractiveness=investment_attractiveness,
        recommendation=recommendation,
        evidence=evidence,
    )

    data = asdict(result)
    data["explanation"] = build_validation_explanation(
        commercial_promise=commercial_promise,
        creative_potential=creative_potential,
        binge_potential=binge_potential,
        test50_value=test50_value,
        investment_attractiveness=investment_attractiveness,
        recommendation=recommendation,
        evidence=evidence,
    )
    return data
