from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.market_positioning_agent import MarketPositioningAgent
from agents.persona_agent import PersonaAgent
from agents.selling_point_agent import SellingPointAgent
from agents.hook_agent import HookAgent
from agents.facebook_creative_agent import FacebookCreativeAgent
from agents.tiktok_creative_agent import TikTokCreativeAgent
from agents.campaign_analysis_agent import CampaignAnalysisAgent
from core.book_loader import load_book_package
from core.file_utils import write_csv, write_json, write_text
from core.markdown import table


def write_hooks_md(path: Path, hooks: dict) -> None:
    lines = [f"# Hooks for {hooks.get('book_id', '')}", ""]
    for h in hooks.get("hooks", []):
        lines.append(f"## {h['hook_id']} 鈥?{h['type']}")
        lines.append("")
        lines.append(h["text"])
        lines.append("")
        lines.append(f"- Emotional Score: {h.get('emotional_score')}")
        lines.append(f"- Clarity Score: {h.get('clarity_score')}")
        lines.append(f"- Click Potential: {h.get('click_potential')}")
        lines.append(f"- Risk: {h.get('risk_level')}")
        lines.append("")
    write_text(path, "\n".join(lines))


def write_facebook_md(path: Path, data: dict) -> None:
    lines = [f"# Facebook / Instagram Ads for {data.get('book_id', '')}", ""]
    lines.append("This file is an execution-ready creative brief. It is not just a hook list.")
    lines.append("")
    for ad in data.get("facebook_ads", []):
        diag = ad.get("appeal_diagnostic") or ad.get("creative_appeal_diagnostic") or {}
        lines.append(f"## {ad['ad_id']} 鈥?{ad.get('angle_type', 'angle')}")
        lines.append("")
        lines.append(f"**Test Purpose:** {ad.get('test_purpose', '')}")
        lines.append(f"**Placement:** {', '.join(ad.get('placement', []))}")
        lines.append(f"**Target Persona:** {ad.get('persona_id', '')} 鈥?{ad.get('target_persona_note', '')}")
        lines.append("")
        lines.append(f"**Headline:** {ad.get('headline', '')}")
        lines.append("")
        lines.append(f"**Primary Text:**\n\n{ad.get('primary_text', '')}")
        lines.append("")
        lines.append(f"**Description:** {ad.get('description', '')}")
        lines.append(f"**CTA:** {ad.get('cta', 'Start Reading')}")
        lines.append(f"**Hook:** {ad.get('hook_id', '')}")
        lines.append(f"**Risk Level:** {ad.get('risk_level', '')}")
        lines.append("")
        lines.append("**Creative Direction:**")
        lines.append(f"- Overall: {ad.get('creative_direction', '')}")
        lines.append(f"- Image/Cover: {ad.get('image_direction', '')}")
        lines.append(f"- Short Video: {ad.get('video_direction', '')}")
        lines.append("")
        lines.append("**Appeal Diagnostics:**")
        for key in ["content_appeal", "hook_appeal", "creative_appeal", "reading_appeal_risk", "improvement_hint"]:
            if diag.get(key):
                lines.append(f"- {key.replace('_', ' ').title()}: {diag.get(key)}")
        if ad.get("compliance_notes"):
            lines.append("")
            lines.append("**Compliance Notes:**")
            for note in ad.get("compliance_notes", []):
                lines.append(f"- {note}")
        lines.append("")
    write_text(path, "\n".join(lines))


def write_tiktok_md(path: Path, data: dict) -> None:
    lines = [f"# TikTok / Reels Scripts for {data.get('book_id', '')}", ""]
    for sc in data.get("tiktok_scripts", []):
        lines.append(f"## {sc['script_id']}")
        lines.append("")
        lines.append(f"**3-second hook:** {sc['three_second_hook']}")
        lines.append("")
        lines.append("**Scene plan:**")
        for item in sc.get("scene_plan", []):
            lines.append(f"- {item}")
        lines.append("")
        lines.append("**Subtitles:**")
        for item in sc.get("subtitle_lines", []):
            lines.append(f"- {item}")
        lines.append("")
        lines.append(f"**Voiceover:** {sc['voiceover']}")
        lines.append("")
        lines.append(f"**CTA:** {sc['ending_cta']}")
        lines.append("")
    write_text(path, "\n".join(lines))


def write_landing_copy_md(path: Path, spec: dict) -> None:
    content = f"""# Landing Page Copy Brief

## Hero Hook

{spec.get('hero_hook', '')}

## Sub Hook

{spec.get('sub_hook', '')}

## CTA

{spec.get('cta_text', 'Start Reading')}

## Trial Chapters

{', '.join(map(str, spec.get('trial_chapters', [])))}

## Chapter Gate

After Chapter {spec.get('chapter_gate_after', 3)}

## Cover Direction

{spec.get('cover_direction', '')}

## Background Direction

{spec.get('background_direction', '')}

## Reading Appeal Design

{json.dumps(spec.get('reading_appeal_design', {}), ensure_ascii=False, indent=2)}
"""
    write_text(path, content)


def write_campaign_md(path: Path, plan: dict) -> None:
    lines = [f"# Campaign Plan: {plan.get('campaign_name')}", ""]
    lines.append(f"**Business Goal:** {plan.get('business_goal')}")
    lines.append(f"**Primary Channel:** {plan.get('primary_channel')}")
    lines.append(f"**Secondary Channel:** {plan.get('secondary_channel')}")
    lines.append(f"**Objective:** {plan.get('objective')}")
    lines.append(f"**Test Period:** {plan.get('test_period_days')} days")
    lines.append(f"**Daily Budget:** ${plan.get('daily_budget_usd_range', [])[0]}-${plan.get('daily_budget_usd_range', [])[1]}")
    lines.append("")
    lines.append("## Facebook Structure")
    for adset in plan.get("facebook_structure", {}).get("ad_sets", []):
        lines.append(f"### {adset['name']}")
        lines.append(f"- Persona: {adset['persona_id']}")
        lines.append(f"- Ads: {', '.join(adset['ads'])}")
    lines.append("")
    lines.append("## Decision Rules")
    for k, v in plan.get("decision_rules", {}).items():
        lines.append(f"- {k}: {v}")
    write_text(path, "\n".join(lines))


def write_checklist_md(path: Path, plan: dict) -> None:
    lines = ["# Manual Ad Ops Checklist", ""]
    for item in plan.get("manual_ops_checklist", []):
        lines.append(f"- [ ] {item}")
    write_text(path, "\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", default="book_001")
    parser.add_argument("--input-root", default=str(ROOT / "input"))
    parser.add_argument("--output-root", default=str(ROOT / "output"))
    args = parser.parse_args()

    book_id = args.book
    input_root = Path(args.input_root)
    output_root = Path(args.output_root)

    print(f"[1/9] Loading book package: {book_id}")
    book = load_book_package(input_root, book_id)

    print("[2/9] Market positioning")
    marketing_profile = MarketPositioningAgent().run(book)
    write_json(output_root / "marketing_profiles" / f"{book_id}_marketing_profile.json", marketing_profile)

    print("[3/9] Personas")
    personas = PersonaAgent().run(book, marketing_profile)
    write_json(output_root / "personas" / f"{book_id}_reader_personas.json", personas)

    print("[4/9] Selling points")
    selling_points = SellingPointAgent().run(book, marketing_profile, personas)
    write_json(output_root / "selling_points" / f"{book_id}_selling_points.json", selling_points)

    print("[5/9] Hooks")
    hooks = HookAgent().run(book, marketing_profile, personas, selling_points)
    write_json(output_root / "hooks" / f"{book_id}_hooks.json", hooks)
    write_hooks_md(output_root / "hooks" / f"{book_id}_hooks.md", hooks)

    print("[6/9] Facebook / Instagram ads")
    fb_ads = FacebookCreativeAgent().run(book, marketing_profile, personas, hooks)
    write_json(output_root / "creatives" / f"{book_id}_facebook_ads.json", fb_ads)
    write_facebook_md(output_root / "creatives" / f"{book_id}_facebook_ads.md", fb_ads)

    print("[7/9] TikTok scripts")
    tt_scripts = TikTokCreativeAgent().run(book, marketing_profile, personas, hooks)
    write_json(output_root / "creatives" / f"{book_id}_tiktok_scripts.json", tt_scripts)
    write_tiktok_md(output_root / "creatives" / f"{book_id}_tiktok_scripts.md", tt_scripts)

    print("[8/9] Landing brief, UTM links and campaign plan")
    campaign_agent = CampaignAnalysisAgent()
    landing_spec = campaign_agent.generate_landing_brief(book, marketing_profile, hooks)
    write_json(output_root / "landing_briefs" / f"{book_id}_landing_page_spec.json", landing_spec)
    write_landing_copy_md(output_root / "landing_briefs" / f"{book_id}_landing_page_copy.md", landing_spec)

    utm_links = campaign_agent.generate_utm_links(book, fb_ads, tt_scripts)
    write_json(output_root / "utm_links" / f"{book_id}_utm_links.json", {"book_id": book_id, "links": utm_links})
    csv_fields = [
        "link_id", "channel", "base_url", "final_url", "utm_source", "utm_medium",
        "utm_campaign", "utm_content", "utm_term", "matched_ad_id", "matched_script_id", "matched_hook_id"
    ]
    write_csv(output_root / "utm_links" / f"{book_id}_utm_links.csv", utm_links, csv_fields)

    campaign_plan = campaign_agent.generate_campaign_plan(book, fb_ads, tt_scripts, utm_links)
    write_json(output_root / "campaign_plans" / f"{book_id}_facebook_campaign_plan.json", campaign_plan)
    write_campaign_md(output_root / "campaign_plans" / f"{book_id}_facebook_campaign_plan.md", campaign_plan)
    write_checklist_md(output_root / "campaign_plans" / f"{book_id}_ad_ops_checklist.md", campaign_plan)

    print("[9/9] Run summary")
    summary = {
        "book_id": book_id,
        "title": book.title,
        "warnings": book.warnings,
        "outputs": {
            "marketing_profile": str(output_root / "marketing_profiles" / f"{book_id}_marketing_profile.json"),
            "personas": str(output_root / "personas" / f"{book_id}_reader_personas.json"),
            "selling_points": str(output_root / "selling_points" / f"{book_id}_selling_points.json"),
            "hooks": str(output_root / "hooks" / f"{book_id}_hooks.json"),
            "facebook_ads": str(output_root / "creatives" / f"{book_id}_facebook_ads.json"),
            "tiktok_scripts": str(output_root / "creatives" / f"{book_id}_tiktok_scripts.json"),
            "landing_spec": str(output_root / "landing_briefs" / f"{book_id}_landing_page_spec.json"),
            "utm_links": str(output_root / "utm_links" / f"{book_id}_utm_links.csv"),
            "campaign_plan": str(output_root / "campaign_plans" / f"{book_id}_facebook_campaign_plan.md"),
        },
    }
    write_json(output_root / f"{book_id}_run_summary.json", summary)
    print("DONE. Outputs generated under:", output_root)


if __name__ == "__main__":
    main()

