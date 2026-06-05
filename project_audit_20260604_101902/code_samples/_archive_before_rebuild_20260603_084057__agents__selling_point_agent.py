from __future__ import annotations

from core.book_loader import BookPackage
from core.llm_client import LLMClient


class SellingPointAgent:
    def __init__(self) -> None:
        self.llm = LLMClient("MODEL_STRATEGY")

    def run(self, book: BookPackage, marketing_profile: dict, personas: dict) -> dict:
        fallback = self._fallback(book)
        return self.llm.generate_json(
            "You extract ad-ready selling points from web novels.",
            f"Book: {book.title}\nMarket: {marketing_profile}\nPersonas: {personas}",
            fallback,
        )

    def _fallback(self, book: BookPackage) -> dict:
        data = [
            ("sp_001", "betrayal", "The heroine was condemned by the empire she saved.", "Lead with injustice and emotional shock."),
            ("sp_002", "revenge", "She returns with power after everyone believed she was dead.", "Promise a comeback and future punishment."),
            ("sp_003", "hidden_identity", "No one recognizes the woman they once destroyed.", "Use mystery and reveal tension."),
            ("sp_004", "power_reversal", "The powerless prisoner becomes the person the empire needs.", "Show the role reversal clearly."),
            ("sp_005", "romantic_tension", "The man who failed her still recognizes her.", "Use regret, danger, and unresolved attraction."),
            ("sp_006", "strong_protagonist", "She survives, adapts, and turns rumors into weapons.", "Position her as a strategic strong heroine."),
            ("sp_007", "family_conflict", "Her personal losses are tied to the empire's lies.", "Use emotional stakes beyond romance."),
            ("sp_008", "kingdom_or_empire_conflict", "Court power, imperial secrets, and royal betrayal drive the story.", "Use dark crown / throne visuals."),
            ("sp_009", "chapter_cliffhanger", "The first three chapters create execution, survival, and confrontation.", "Structure ads around the chapter-to-chapter curiosity gap."),
        ]
        selling_points = []
        for sid, typ, summary, angle in data:
            selling_points.append({
                "selling_point_id": sid,
                "type": typ,
                "summary": summary,
                "ad_angle": angle,
                "evidence_from_story": "Derived from sample chapters and story bible summary.",
                "best_for_channels": ["facebook", "instagram", "tiktok"],
                "risk_level": "low",
                "appeal_diagnostic": {
                    "content_appeal": "Strong" if typ in ["betrayal", "revenge", "romantic_tension"] else "Medium",
                    "improvement_hint": "Turn this into a concrete scene-based hook, not abstract worldbuilding."
                }
            })
        return {"book_id": book.book_id, "selling_points": selling_points}
