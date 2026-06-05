from __future__ import annotations

from core.book_loader import BookPackage
from core.llm_client import LLMClient


class PersonaAgent:
    def __init__(self) -> None:
        self.llm = LLMClient("MODEL_STRATEGY")

    def run(self, book: BookPackage, marketing_profile: dict) -> dict:
        fallback = self._fallback(book)
        return self.llm.generate_json(
            "You generate paid-social reader personas for English web novels.",
            f"Book: {book.title}\nMarket profile: {marketing_profile}",
            fallback,
        )

    def _fallback(self, book: BookPackage) -> dict:
        personas = [
            {
                "persona_id": "persona_001",
                "name": "Facebook Fantasy Romance Reader",
                "platform": "facebook",
                "age_range": "25-44",
                "gender_tendency": "female-skewed",
                "interests": ["fantasy romance", "romance novels", "web novels", "Kindle romance"],
                "emotional_triggers": ["betrayal", "slow-burn tension", "strong heroine", "revenge"],
                "content_preferences": ["clear emotional stakes", "cinematic conflict", "high-status male lead tension"],
                "avoid_angles": ["complex lore before emotion", "overly vague fantasy terms"],
                "recommended_hook_types": ["betrayal_hook", "revenge_hook", "romantic_tension_hook"],
                "recommended_creative_style": "emotional, direct, book-ad style with a strong first sentence"
            },
            {
                "persona_id": "persona_002",
                "name": "Facebook Web Novel Reader",
                "platform": "facebook",
                "age_range": "18-44",
                "gender_tendency": "mixed",
                "interests": ["GoodNovel", "Dreame", "Wattpad", "serialized fiction"],
                "emotional_triggers": ["cliffhanger", "identity reveal", "chapter gate curiosity"],
                "content_preferences": ["fast premise", "clear revenge arc", "continue reading CTA"],
                "avoid_angles": ["literary copy", "slow synopsis"],
                "recommended_hook_types": ["chapter_cliffhanger_hook", "hidden_identity_hook"],
                "recommended_creative_style": "serialized web-novel teaser style"
            },
            {
                "persona_id": "persona_003",
                "name": "Broad Female 25-44 Reader",
                "platform": "facebook",
                "age_range": "25-44",
                "gender_tendency": "female-skewed",
                "interests": ["broad reading audience"],
                "emotional_triggers": ["betrayal", "comeback", "romantic regret"],
                "content_preferences": ["easy-to-understand conflict", "emotional injustice"],
                "avoid_angles": ["too many names", "unclear fantasy mechanics"],
                "recommended_hook_types": ["betrayal_hook", "power_reversal_hook"],
                "recommended_creative_style": "simple, emotional, highly readable"
            },
            {
                "persona_id": "persona_004",
                "name": "TikTok Emotional Hook Reader",
                "platform": "tiktok",
                "age_range": "18-34",
                "gender_tendency": "female-skewed",
                "interests": ["BookTok", "romantasy", "dark fantasy edits"],
                "emotional_triggers": ["first-line shock", "betrayal reveal", "he regretted it too late"],
                "content_preferences": ["short subtitles", "visual mood", "fast reversal"],
                "avoid_angles": ["slow voiceover", "too much backstory"],
                "recommended_hook_types": ["tiktok_three_second_hook", "romantic_tension_hook"],
                "recommended_creative_style": "short subtitle-driven video with dramatic emotional reversal"
            },
            {
                "persona_id": "persona_005",
                "name": "TikTok BookTok Style Reader",
                "platform": "tiktok",
                "age_range": "18-30",
                "gender_tendency": "female-skewed",
                "interests": ["BookTok recommendations", "romantasy quotes", "reading aesthetics"],
                "emotional_triggers": ["queen energy", "enemy tension", "revenge return"],
                "content_preferences": ["aesthetic text overlays", "moody covers", "quote-style hooks"],
                "avoid_angles": ["generic ads", "hard-sell CTA too early"],
                "recommended_hook_types": ["strong_female_lead_hook", "hidden_identity_hook"],
                "recommended_creative_style": "aesthetic, quote-like, emotional micro-story"
            }
        ]
        return {"book_id": book.book_id, "personas": personas}
