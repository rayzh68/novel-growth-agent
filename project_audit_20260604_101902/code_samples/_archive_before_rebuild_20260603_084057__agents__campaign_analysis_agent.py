from __future__ import annotations

from urllib.parse import urlencode

from core.book_loader import BookPackage
from core.file_utils import slugify


class CampaignAnalysisAgent:
    def generate_landing_brief(self, book: BookPackage, marketing_profile: dict, hooks: dict) -> dict:
        hero = ""
        for h in hooks.get("hooks", []):
            if h.get("type") == "landing_page_hero_hook":
                hero = h["text"]
                break
        if not hero and hooks.get("hooks"):
            hero = hooks["hooks"][0]["text"]

        return {
            "book_id": book.book_id,
            "page_type": "single_book_landing_page",
            "recommended_template": "netflix_dreame_tiktok_dark",
            "hero_hook": hero,
            "sub_hook": marketing_profile.get("market_positioning", ""),
            "cta_text": "Start Reading",
            "trial_chapters": [1, 2, 3],
            "chapter_gate_after": 3,
            "ad_unlock_enabled": True,
            "cover_direction": "dark crown, betrayed heroine, royal fantasy, red-black-gold mood",
            "background_direction": "cinematic royal hall, shadows, masked ball, throne silhouette",
            "character_card_enabled": True,
            "recommended_sections": [
                "Hero",
                "Genre Tags",
                "Story Teaser",
                "Read Preview",
                "Character Cards",
                "Chapter Gate",
                "Continue Reading CTA"
            ],
            "tracking_events": [
                "landing_view", "start_reading_click", "read_start", "chapter_1_finish",
                "chapter_3_finish", "gate_view", "unlock_click", "ad_watch_start",
                "ad_watch_complete", "subscribe_click"
            ],
            "reading_appeal_design": {
                "reading_appeal_goal": "Convert paid clicks into chapter 1 and chapter 3 finishers.",
                "risk": "If the page explains too much worldbuilding before the CTA, read start may fall.",
                "improvement_hint": "Keep the hero hook, Start Reading button, and first chapter entry above the fold."
            }
        }

    def generate_utm_links(self, book: BookPackage, facebook_ads: dict, tiktok_scripts: dict) -> list[dict]:
        links = []
        base_url = book.base_url

        for ad in facebook_ads.get("facebook_ads", []):
            term = "female_25_44_fantasy_romance" if ad.get("persona_id") == "persona_001" else "broad_female_25_44"
            content = f"{ad['ad_id']}_{ad.get('hook_id', 'hook')}"
            params = {
                "utm_source": "facebook",
                "utm_medium": "paid_social",
                "utm_campaign": f"{book.book_id}_fb_test_001",
                "utm_content": slugify(content),
                "utm_term": term,
            }
            links.append({
                "link_id": f"utm_{len(links)+1:03d}",
                "channel": "facebook",
                "base_url": base_url,
                "final_url": base_url + "?" + urlencode(params),
                **params,
                "matched_ad_id": ad["ad_id"],
                "matched_hook_id": ad.get("hook_id", "")
            })

        for sc in tiktok_scripts.get("tiktok_scripts", []):
            content = f"{sc['script_id']}_{sc.get('hook_id', 'hook')}"
            params = {
                "utm_source": "tiktok",
                "utm_medium": "paid_social",
                "utm_campaign": f"{book.book_id}_tt_test_001",
                "utm_content": slugify(content),
                "utm_term": "booktok_emotional",
            }
            links.append({
                "link_id": f"utm_{len(links)+1:03d}",
                "channel": "tiktok",
                "base_url": base_url,
                "final_url": base_url + "?" + urlencode(params),
                **params,
                "matched_script_id": sc["script_id"],
                "matched_hook_id": sc.get("hook_id", "")
            })
        return links

    def generate_campaign_plan(self, book: BookPackage, facebook_ads: dict, tiktok_scripts: dict, utm_links: list[dict]) -> dict:
        return {
            "book_id": book.book_id,
            "campaign_name": f"{book.book_id}_FB_Test_001",
            "primary_channel": "facebook",
            "secondary_channel": "tiktok",
            "business_goal": "Find positive-ROI promotion combinations as quickly as possible.",
            "objective": "Landing Page View / Traffic",
            "test_period_days": 3,
            "daily_budget_usd_range": [20, 50],
            "facebook_structure": {
                "campaign": f"{book.book_id}_FB_Test_001",
                "ad_sets": [
                    {"name": "Fantasy Romance Interest", "persona_id": "persona_001", "ads": [a["ad_id"] for a in facebook_ads.get("facebook_ads", [])[:5]]},
                    {"name": "Web Novel / Reading Interest", "persona_id": "persona_002", "ads": [a["ad_id"] for a in facebook_ads.get("facebook_ads", [])[5:10]]},
                    {"name": "Broad Female 25-44", "persona_id": "persona_003", "ads": [a["ad_id"] for a in facebook_ads.get("facebook_ads", [])[:5]]}
                ]
            },
            "tiktok_test": {
                "goal": "Validate 3-second hooks and emotional reversal angles.",
                "scripts": [s["script_id"] for s in tiktok_scripts.get("tiktok_scripts", [])]
            },
            "decision_rules": {
                "24h": "Kill or rewrite ads with low CTR and high CPC.",
                "48_72h": "Check read_start, chapter_1_finish and chapter_3_finish.",
                "3_7d": "Validate unlock intent, revenue per click, ROI and net profit."
            },
            "utm_link_count": len(utm_links),
            "manual_ops_checklist": [
                "Confirm rights_info.json before paid launch.",
                "Create Facebook Traffic or Landing Page View campaign.",
                "Create three ad sets: Fantasy Romance, Web Novel/Reading, Broad Female 25-44.",
                "Use generated UTM final URLs for each ad.",
                "Run first test for 24 hours before major decisions.",
                "Export ad report CSV and site events CSV after 48-72 hours."
            ]
        }
