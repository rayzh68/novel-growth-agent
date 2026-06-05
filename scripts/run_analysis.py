from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def safe_div(a: float, b: float) -> float:
    try:
        if b == 0:
            return 0.0
        return float(a) / float(b)
    except Exception:
        return 0.0


def read_csv_folder(folder: Path) -> pd.DataFrame:
    if not folder.exists():
        return pd.DataFrame()

    files = sorted(folder.glob("*.csv"))
    if not files:
        return pd.DataFrame()

    frames = []
    error_rows = []

    for file in files:
        try:
            df = pd.read_csv(file)
            df["_source_file"] = file.name
            frames.append(df)
        except Exception as exc:
            error_rows.append({"file": file.name, "error": str(exc)})

    if error_rows:
        err_dir = ROOT / "output" / "reports"
        ensure_dir(err_dir)
        pd.DataFrame(error_rows).to_csv(err_dir / "error_rows.csv", index=False)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


def normalize_columns(df: pd.DataFrame, required: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in required:
        if col not in out.columns:
            out[col] = 0
    return out


def numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0)
    return out


def write_json(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def fmt_num(value: Any, digits: int = 4) -> str:
    try:
        v = float(value)
        if abs(v) >= 100:
            return f"{v:.0f}"
        if abs(v) >= 10:
            return f"{v:.2f}"
        return f"{v:.{digits}f}".rstrip("0").rstrip(".")
    except Exception:
        return str(value)


def markdown_table(rows: list[dict[str, Any]], cols: list[str]) -> str:
    if not rows:
        return "- None"

    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join(["---"] * len(cols)) + " |"
    body = []

    for row in rows:
        body.append("| " + " | ".join(fmt_num(row.get(col, "")) for col in cols) + " |")

    return "\n".join([header, sep] + body)


def build_no_data_outputs(book: str, round_id: str) -> None:
    report = {
        "book_id": book,
        "round": round_id,
        "current_stage": "no_data",
        "final_goal": "maximize net profit in the shortest practical time",
        "positive_roi_candidate": False,
        "executive_decision": "No data imported. Do not make scaling decisions.",
        "recommendations": [
            "Import ad report CSV into data_reports/ad_reports.",
            "Import site event CSV into data_reports/site_events.",
            "Run python main.py analyze again."
        ],
    }

    next_round = {
        "book_id": book,
        "round": round_id,
        "keep": [],
        "rewrite": [],
        "kill_or_pause": [],
        "budget_actions": ["Do not scale budget until report data is imported."],
        "creative_actions": ["Keep current assets as draft only."],
        "landing_page_actions": ["Confirm event tracking before paid traffic."]
    }

    feedback = {
        "book_id": book,
        "test_round": round_id,
        "best_hooks": [],
        "worst_hooks": [],
        "best_personas": [],
        "weak_points": ["No report data imported yet."],
        "recommendations_for_content_team": [],
        "recommendations_for_site_team": ["Confirm tracking events are exported as CSV."],
        "recommendations_for_growth_team": ["Import Facebook/TikTok and site event data first."],
    }

    write_json(ROOT / "output" / "reports" / f"{book}_growth_report.json", report)
    write_text(ROOT / "output" / "reports" / f"{book}_growth_report.md", "# Growth Report\n\nNo ad or site event data found.\n")
    write_json(ROOT / "output" / "next_rounds" / f"{book}_next_round_plan.json", next_round)
    write_text(ROOT / "output" / "next_rounds" / f"{book}_next_round_plan.md", "# Next Round Plan\n\nNo data available yet.\n")
    write_json(ROOT / "output" / "feedback" / f"{book}_growth_feedback.json", feedback)


def classify_row(row: dict[str, Any]) -> tuple[str, str, list[str]]:
    source = str(row.get("utm_source", "")).lower()
    roi = float(row.get("roi", 0))
    ctr = float(row.get("ctr", 0))
    cpc = float(row.get("cpc", 0))
    read_start = float(row.get("read_start_rate", 0))
    ch1 = float(row.get("chapter_1_finish_rate", 0))
    ch3 = float(row.get("chapter_3_finish_rate", 0))
    unlock = float(row.get("unlock_click_rate", 0))
    net_profit = float(row.get("net_profit", 0))

    issues: list[str] = []

    high_ctr = ctr >= 0.025
    low_ctr = ctr < 0.015
    high_cpc = cpc > 0.8
    good_read_start = read_start >= 0.35
    weak_read_start = read_start < 0.35
    good_ch3 = ch3 >= 0.12
    weak_ch3 = ch3 < 0.10
    weak_roi = roi < 1.0
    positive_roi = roi >= 1.1

    if positive_roi and net_profit > 0:
        return (
            "scale_candidate",
            "Positive ROI and positive net profit. Use controlled scaling only.",
            ["scale_budget_controlled", "clone_winning_hook", "protect_tracking_quality"]
        )

    if high_ctr and weak_roi and net_profit < 0:
        if source == "tiktok":
            issues.append("TikTok has strong click signal but weak ROI. Do not scale only because CTR is high.")
        else:
            issues.append("Strong click signal but weak ROI. The promise may not convert into revenue.")
        if weak_ch3:
            issues.append("Chapter 3 continuation is weak. Reading depth may not support monetization.")
        if unlock < 0.02:
            issues.append("Unlock or gate intent is weak. Monetization path needs review.")
        return (
            "high_click_low_roi",
            "High CTR but low ROI and negative net profit. Rewrite creative or landing continuation before any scaling.",
            ["rewrite_creative", "check_audience_quality", "check_landing_message_match", "verify_monetization_path"] + issues
        )

    if high_ctr and weak_read_start:
        return (
            "high_click_low_reading",
            "High CTR but weak read start. The ad may be over-promising or the landing page is not matching the ad.",
            ["rewrite_landing_hero", "match_ad_hook_to_landing_page", "check_first_screen"]
        )

    if good_read_start and weak_ch3 and weak_roi:
        return (
            "fix_reading_continuation",
            "Readers start, but they do not continue deep enough. The first three chapters may not deliver the ad promise.",
            ["review_chapter_opening", "strengthen_chapter_1_to_3_hooks", "align_content_with_winning_ad"]
        )

    if low_ctr and good_read_start:
        return (
            "rewrite_hook_keep_audience",
            "Audience quality may be valid, but the hook is not strong enough to attract clicks.",
            ["rewrite_hook", "keep_audience_test", "test_betrayal_revenge_identity_variants"]
        )

    if low_ctr and high_cpc:
        return (
            "kill_or_pause",
            "Low CTR and high CPC. This combination is inefficient for cold traffic.",
            ["pause_or_kill", "do_not_retest_without_new_hook"]
        )

    if good_ch3 and weak_roi:
        return (
            "keep_and_iterate",
            "Reading quality has some signal, but ROI is not validated yet.",
            ["keep_small_budget", "test_new_gate_or_cta", "improve_revenue_path"]
        )

    return (
        "observe",
        "Insufficient signal for scaling or killing. Keep budget stable and collect more data.",
        ["observe_more_data"]
    )


def build_analysis(book: str, round_id: str) -> None:
    ad_dir = ROOT / "data_reports" / "ad_reports"
    site_dir = ROOT / "data_reports" / "site_events"

    ads = read_csv_folder(ad_dir)
    site = read_csv_folder(site_dir)

    if ads.empty and site.empty:
        build_no_data_outputs(book, round_id)
        print(f"DONE. No data outputs generated under: {ROOT / 'output'}")
        return

    ad_required = [
        "utm_source", "utm_campaign", "utm_content", "utm_term",
        "impressions", "clicks", "spend", "landing_views"
    ]
    site_required = [
        "utm_source", "utm_campaign", "utm_content", "utm_term",
        "landing_view", "start_reading_click", "read_start",
        "chapter_1_finish", "chapter_3_finish", "gate_view",
        "unlock_click", "ad_watch_start", "ad_watch_complete",
        "subscribe_click", "revenue"
    ]

    ads = normalize_columns(ads, ad_required)
    site = normalize_columns(site, site_required)

    ads = numeric(ads, ["impressions", "clicks", "spend", "landing_views"])
    site = numeric(site, [
        "landing_view", "start_reading_click", "read_start",
        "chapter_1_finish", "chapter_3_finish", "gate_view",
        "unlock_click", "ad_watch_start", "ad_watch_complete",
        "subscribe_click", "revenue"
    ])

    keys = ["utm_source", "utm_campaign", "utm_content", "utm_term"]

    ad_agg = ads.groupby(keys, dropna=False)[["impressions", "clicks", "spend", "landing_views"]].sum().reset_index()
    site_agg = site.groupby(keys, dropna=False)[[
        "landing_view", "start_reading_click", "read_start",
        "chapter_1_finish", "chapter_3_finish", "gate_view",
        "unlock_click", "ad_watch_start", "ad_watch_complete",
        "subscribe_click", "revenue"
    ]].sum().reset_index()

    if ad_agg.empty:
        merged = site_agg.copy()
        for col in ["impressions", "clicks", "spend", "landing_views"]:
            merged[col] = 0
    elif site_agg.empty:
        merged = ad_agg.copy()
        for col in [
            "landing_view", "start_reading_click", "read_start",
            "chapter_1_finish", "chapter_3_finish", "gate_view",
            "unlock_click", "ad_watch_start", "ad_watch_complete",
            "subscribe_click", "revenue"
        ]:
            merged[col] = 0
    else:
        merged = ad_agg.merge(site_agg, on=keys, how="outer").fillna(0)

    records: list[dict[str, Any]] = []

    for _, row in merged.iterrows():
        impressions = float(row.get("impressions", 0))
        clicks = float(row.get("clicks", 0))
        spend = float(row.get("spend", 0))
        landing_views = max(float(row.get("landing_views", 0)), float(row.get("landing_view", 0)))
        read_start = float(row.get("read_start", 0))
        ch1 = float(row.get("chapter_1_finish", 0))
        ch3 = float(row.get("chapter_3_finish", 0))
        gate = float(row.get("gate_view", 0))
        unlock = float(row.get("unlock_click", 0))
        ad_start = float(row.get("ad_watch_start", 0))
        ad_complete = float(row.get("ad_watch_complete", 0))
        revenue = float(row.get("revenue", 0))

        ctr = safe_div(clicks, impressions)
        cpc = safe_div(spend, clicks)
        landing_view_rate = safe_div(landing_views, clicks)
        read_start_rate = safe_div(read_start, landing_views)
        ch1_rate = safe_div(ch1, read_start)
        ch3_rate = safe_div(ch3, read_start)
        gate_rate = safe_div(gate, read_start)
        unlock_rate = safe_div(unlock, gate)
        ad_complete_rate = safe_div(ad_complete, ad_start)
        revenue_per_click = safe_div(revenue, clicks)
        revenue_per_landing_view = safe_div(revenue, landing_views)
        revenue_per_1000_landing_views = revenue_per_landing_view * 1000
        roi = safe_div(revenue, spend)
        net_profit = revenue - spend

        appeal_signal = (
            min(ctr / 0.03, 1) * 0.20
            + min((1 / max(cpc, 0.01)) / 2, 1) * 0.15
            + min(read_start_rate / 0.35, 1) * 0.20
            + min(ch1_rate / 0.25, 1) * 0.20
            + min(ch3_rate / 0.12, 1) * 0.15
            + min(unlock_rate / 0.02, 1) * 0.10
        )

        item = {
            "utm_source": row.get("utm_source", ""),
            "utm_campaign": row.get("utm_campaign", ""),
            "utm_content": row.get("utm_content", ""),
            "utm_term": row.get("utm_term", ""),
            "impressions": impressions,
            "clicks": clicks,
            "spend": spend,
            "ctr": ctr,
            "cpc": cpc,
            "landing_views": landing_views,
            "landing_view_rate": landing_view_rate,
            "read_start_rate": read_start_rate,
            "chapter_1_finish_rate": ch1_rate,
            "chapter_3_finish_rate": ch3_rate,
            "gate_view_rate": gate_rate,
            "unlock_click_rate": unlock_rate,
            "ad_watch_complete_rate": ad_complete_rate,
            "revenue": revenue,
            "revenue_per_click": revenue_per_click,
            "revenue_per_1000_landing_views": revenue_per_1000_landing_views,
            "roi": roi,
            "net_profit": net_profit,
            "appeal_signal": appeal_signal,
        }

        decision, diagnosis, actions = classify_row(item)
        item["decision"] = decision
        item["diagnosis"] = diagnosis
        item["recommended_actions"] = actions
        records.append(item)

    records = sorted(records, key=lambda x: (x["roi"], x["net_profit"], x["appeal_signal"]), reverse=True)

    positive = [r for r in records if r["decision"] == "scale_candidate"]
    keep = [r for r in records if r["decision"] in ["scale_candidate", "keep_and_iterate"]]
    rewrite = [r for r in records if r["decision"] in [
        "high_click_low_roi",
        "high_click_low_reading",
        "rewrite_hook_keep_audience",
        "fix_reading_continuation",
    ]]
    kill = [r for r in records if r["decision"] == "kill_or_pause"]
    observe = [r for r in records if r["decision"] == "observe"]

    if positive:
        stage = "profit_validation_or_scale_candidate"
        executive_decision = "Positive ROI candidate found. Use controlled scaling only."
    else:
        stage = "reading_quality_or_cold_start_validation"
        executive_decision = "No positive ROI candidate yet. Continue controlled testing and do not scale."

    budget_actions: list[str] = []
    if positive:
        budget_actions.append("Increase budget for scale candidates by 20-30 percent after confirming tracking stability.")
    if rewrite:
        budget_actions.append("Keep rewrite candidates at low budget only. Do not scale until ROI and reading depth improve.")
    if kill:
        budget_actions.append("Pause or kill combinations with low CTR, high CPC, and weak commercial signal.")
    if not budget_actions:
        budget_actions.append("Keep budget stable until more data is collected.")

    creative_actions: list[str] = []
    if positive:
        creative_actions.append("Clone each winning Facebook hook into 5 new variants.")
        creative_actions.append("Generate separate variants for betrayal, revenge, hidden identity, and power reversal.")
    if rewrite:
        creative_actions.append("Rewrite high-click low-ROI creatives. Keep the strong opening hook but change middle promise, CTA, audience, or landing match.")
        creative_actions.append("For TikTok high-click low-ROI scripts, do not increase budget. Rebuild script middle section and verify reading continuation.")
    if kill:
        creative_actions.append("Do not reuse killed hooks without a new angle and new audience.")
    if observe:
        creative_actions.append("For observe items, keep budget stable and wait for more data before decision.")

    landing_page_actions = [
        "Keep CTA above the fold.",
        "Match landing hero hook with the winning ad hook.",
        "Track read_start, chapter_1_finish, chapter_3_finish, gate_view, unlock_click, ad_watch_complete, and revenue.",
    ]

    if rewrite:
        landing_page_actions.append("For rewrite candidates, check if the landing page promise matches the ad promise.")
        landing_page_actions.append("If Chapter 3 continuation is weak, review whether the first three chapters deliver the same emotional promise as the ad.")

    report = {
        "book_id": book,
        "round": round_id,
        "current_stage": stage,
        "final_goal": "maximize net profit in the shortest practical time",
        "positive_roi_candidate": bool(positive),
        "executive_decision": executive_decision,
        "top_combinations": records[:10],
        "scale_candidates": positive,
        "keep_or_iterate_candidates": keep,
        "rewrite_candidates": rewrite,
        "kill_or_pause_candidates": kill,
        "observe_candidates": observe,
        "budget_actions": budget_actions,
        "creative_actions": creative_actions,
        "landing_page_actions": landing_page_actions,
        "next_decision_timeline": {
            "24_hours": "Check CTR and CPC signal.",
            "48_72_hours": "Check read start and chapter finish quality.",
            "3_7_days": "Check revenue per click, ROI, and net profit."
        },
    }

    next_round = {
        "book_id": book,
        "round": round_id,
        "keep": [r["utm_content"] for r in keep],
        "rewrite": [
            {
                "utm_content": r["utm_content"],
                "decision": r["decision"],
                "diagnosis": r["diagnosis"],
                "actions": r["recommended_actions"]
            }
            for r in rewrite
        ],
        "kill_or_pause": [r["utm_content"] for r in kill],
        "observe": [r["utm_content"] for r in observe],
        "budget_actions": budget_actions,
        "creative_actions": creative_actions,
        "landing_page_actions": landing_page_actions,
    }

    feedback = {
        "book_id": book,
        "test_round": round_id,
        "best_hooks": [r["utm_content"] for r in records[:3]],
        "worst_hooks": [r["utm_content"] for r in records[-3:]],
        "best_personas": list({str(r.get("utm_term", "")) for r in records[:3]}),
        "weak_points": [
            "Review high_click_low_roi combinations for mismatch between click promise and revenue path.",
            "Review high_click_low_reading combinations for mismatch between ad hook and landing or chapter opening.",
            "Review low CTR combinations for weak hook or wrong audience.",
            "Review low ROI combinations for monetization or gate placement issues."
        ],
        "recommendations_for_content_team": [
            "Strengthen the first chapter opening if read_start or chapter_1_finish is weak.",
            "Make the first three chapters deliver the same promise used in the winning ad hook.",
            "If TikTok has high clicks but weak Chapter 3 continuation, check whether the script promise is too broad or mismatched."
        ],
        "recommendations_for_site_team": [
            "Ensure UTM parameters are saved with each session.",
            "Ensure all core reading and unlock events are exported to CSV.",
            "Match landing page hero text with the active ad hook for each UTM campaign."
        ],
        "recommendations_for_growth_team": budget_actions + creative_actions,
    }

    write_json(ROOT / "output" / "reports" / f"{book}_growth_report.json", report)
    write_json(ROOT / "output" / "next_rounds" / f"{book}_next_round_plan.json", next_round)
    write_json(ROOT / "output" / "feedback" / f"{book}_growth_feedback.json", feedback)

    cols = [
        "utm_source", "utm_campaign", "utm_content", "impressions", "clicks", "spend",
        "ctr", "cpc", "read_start_rate", "chapter_1_finish_rate",
        "chapter_3_finish_rate", "unlock_click_rate", "revenue", "roi",
        "net_profit", "appeal_signal", "decision"
    ]

    md: list[str] = []
    md.append(f"# Growth Report - {book} / {round_id}\n")
    md.append(f"**Current Stage:** {stage}\n")
    md.append("**Final Goal:** maximize net profit in the shortest practical time\n")
    md.append(f"**Positive ROI Candidate:** {bool(positive)}\n")
    md.append(f"**Executive Decision:** {executive_decision}\n")

    md.append("\n## Top Combinations\n")
    md.append(markdown_table(records, cols))

    md.append("\n\n## Scale Candidates\n")
    md.append("\n".join([f"- {r['utm_content']} | ROI={r['roi']:.2f} | Net Profit={r['net_profit']:.2f} | Action: controlled scale 20-30%" for r in positive]) or "- None")

    md.append("\n\n## Keep or Iterate Candidates\n")
    md.append("\n".join([f"- {r['utm_content']} | Decision={r['decision']}" for r in keep]) or "- None")

    md.append("\n\n## Rewrite Candidates\n")
    if rewrite:
        for r in rewrite:
            md.append(f"- {r['utm_content']} | Decision={r['decision']}")
            md.append(f"  - Diagnosis: {r['diagnosis']}")
            for action in r["recommended_actions"]:
                md.append(f"  - Action: {action}")
    else:
        md.append("- None")

    md.append("\n\n## Kill or Pause Candidates\n")
    md.append("\n".join([f"- {r['utm_content']} | CTR={r['ctr']:.3f} | CPC={r['cpc']:.2f} | ROI={r['roi']:.2f}" for r in kill]) or "- None")

    md.append("\n\n## Observe Candidates\n")
    md.append("\n".join([f"- {r['utm_content']} | More data needed" for r in observe]) or "- None")

    md.append("\n\n## Budget Actions\n")
    md.append("\n".join([f"- {x}" for x in budget_actions]))

    md.append("\n\n## Creative Actions\n")
    md.append("\n".join([f"- {x}" for x in creative_actions]))

    md.append("\n\n## Landing Page Actions\n")
    md.append("\n".join([f"- {x}" for x in landing_page_actions]))

    md.append("\n\n## Appeal Diagnostics\n")
    md.append("- Appeal diagnostics locate whether the issue is content, hook, creative, landing page, reading continuation, or monetization.")
    md.append("- This is not the final goal. The final goal is net profit and ROI.")
    md.append("- High CTR with low ROI is not a win. It is a rewrite or monetization diagnosis candidate.")

    md.append("\n\n## Next Decision Timeline\n")
    md.append("- 24 hours: Check CTR and CPC signal.")
    md.append("- 48-72 hours: Check read start and chapter finish quality.")
    md.append("- 3-7 days: Check revenue per click, ROI, and net profit.")

    write_text(ROOT / "output" / "reports" / f"{book}_growth_report.md", "\n".join(md))

    next_md: list[str] = []
    next_md.append(f"# Next Round Plan - {book} / {round_id}\n")

    next_md.append("## Keep\n")
    next_md.append("\n".join([f"- {x}" for x in next_round["keep"]]) or "- None")

    next_md.append("\n\n## Rewrite\n")
    if next_round["rewrite"]:
        for item in next_round["rewrite"]:
            next_md.append(f"- {item['utm_content']} | {item['decision']}")
            next_md.append(f"  - Diagnosis: {item['diagnosis']}")
            for action in item["actions"]:
                next_md.append(f"  - Action: {action}")
    else:
        next_md.append("- None")

    next_md.append("\n\n## Kill or Pause\n")
    next_md.append("\n".join([f"- {x}" for x in next_round["kill_or_pause"]]) or "- None")

    next_md.append("\n\n## Observe\n")
    next_md.append("\n".join([f"- {x}" for x in next_round["observe"]]) or "- None")

    next_md.append("\n\n## Budget Actions\n")
    next_md.append("\n".join([f"- {x}" for x in budget_actions]))

    next_md.append("\n\n## Creative Actions\n")
    next_md.append("\n".join([f"- {x}" for x in creative_actions]))

    next_md.append("\n\n## Landing Page Actions\n")
    next_md.append("\n".join([f"- {x}" for x in landing_page_actions]))

    write_text(ROOT / "output" / "next_rounds" / f"{book}_next_round_plan.md", "\n".join(next_md))

    print(f"DONE. Analysis outputs generated under: {ROOT / 'output'}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", default="book_001")
    parser.add_argument("--round", default="round_001", dest="round_id")
    args = parser.parse_args(argv)
    build_analysis(args.book, args.round_id)


if __name__ == "__main__":
    main()
