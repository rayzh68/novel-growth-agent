from __future__ import annotations

from core.book_loader import BookPackage
from core.llm_client import LLMClient


class TikTokCreativeAgent:
    def __init__(self) -> None:
        self.llm = LLMClient("MODEL_CREATIVE")

    def run(self, book: BookPackage, marketing_profile: dict, personas: dict, hooks: dict) -> dict:
        fallback = self._fallback(book, hooks)
        return self.llm.generate_json(
            "You generate TikTok/Reels/Shorts scripts for English web novels.",
            f"Book: {book.title}\nMarket: {marketing_profile}\nPersonas: {personas}\nHooks: {hooks}",
            fallback,
        )

    def _fallback(self, book: BookPackage, hooks: dict) -> dict:
        selected = hooks.get("hooks", [])[:10]
        scripts = []
        for i, hook in enumerate(selected, start=1):
            scripts.append({
                "script_id": f"tt_script_{i:03d}",
                "duration_seconds": 20,
                "three_second_hook": hook["text"].split(".")[0] + ".",
                "scene_plan": [
                    "0-3s: dark crown / execution scene text overlay",
                    "3-8s: heroine in chains, crowd cheering",
                    "8-14s: years later, masked woman returns to royal hall",
                    "14-20s: male lead recognizes her; CTA appears"
                ],
                "subtitle_lines": [
                    hook["text"],
                    "She survived what they did to her.",
                    "Now the empire wants her back.",
                    "Start reading now."
                ],
                "voiceover": f"{hook['text']} She was supposed to disappear. Instead, she came back for the crown.",
                "visual_direction": "dark romantasy edit, crown, masquerade, black silk, red-gold lighting",
                "ending_cta": "Start reading now.",
                "hook_id": hook["hook_id"],
                "persona_id": "persona_004",
                "risk_level": "low",
                "creative_appeal_diagnostic": {
                    "creative_appeal": "Good for 3-second hook testing",
                    "possible_issue": "TikTok may drive curiosity clicks but weaker reading depth; validate chapter finish rates.",
                    "improvement_hint": "If clicks are high but reading is poor, make the subtitle more book-specific and less generic."
                }
            })
        return {"book_id": book.book_id, "tiktok_scripts": scripts}
