from __future__ import annotations

from core.book_loader import BookPackage
from core.llm_client import LLMClient


class MarketPositioningAgent:
    def __init__(self) -> None:
        self.llm = LLMClient("MODEL_STRATEGY")

    def run(self, book: BookPackage) -> dict:
        fallback = self._fallback(book)
        return self.llm.generate_json(
            "You generate market positioning for English serialized web novels.",
            f"Book title: {book.title}\nGenres: {book.genre_text}\nFirst chapters: {book.sample_chapters}",
            fallback,
        )

    def _fallback(self, book: BookPackage) -> dict:
        genres = book.manifest.get("genre", [])
        title = book.title
        return {
            "book_id": book.book_id,
            "title": title,
            "primary_genre": "revenge fantasy romance" if "fantasy" in genres else "serialized romance fantasy",
            "secondary_genres": ["hidden identity", "royal betrayal", "power reversal"],
            "market_positioning": f"{title} is a revenge-driven fantasy romance for readers who respond to betrayal, hidden power, and emotional power reversal.",
            "north_star_goal": "maximize net profit per day by finding positive-ROI promotion combinations fast",
            "core_emotions": ["betrayal", "revenge", "power reversal", "forbidden tension", "identity reveal"],
            "core_conflicts": ["framed heroine vs empire", "old betrayal vs unresolved love", "hidden identity vs royal court"],
            "recommended_channels": ["facebook", "instagram", "tiktok"],
            "facebook_priority": True,
            "tiktok_priority": True,
            "content_appeal_diagnostics": {
                "content_appeal": "Strong commercial potential if the first three chapters emphasize betrayal, survival, return, and emotional confrontation.",
                "market_risk": "If the opening spends too much time on worldbuilding, paid traffic may drop before chapter 1 finish.",
                "improvement_focus": ["make the first conflict visible immediately", "keep the revenge promise clear", "avoid slow exposition before the first CTA"]
            },
            "risk_angles": ["over-explicit romance bait", "claims about scenes not in the book", "unauthorized IP comparisons"],
            "do_not_use_angles": ["Game of Thrones-style official comparison", "explicit adult bait", "celebrity comparisons"],
            "warnings": book.warnings,
        }
