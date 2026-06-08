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

    commercial_promise = clamp_score(
        score_from_count(question_pressure + conflict_pressure, low=5, high=35)
    )

    creative_potential = clamp_score(
        score_from_count(creative_hooks, low=2, high=18)
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
