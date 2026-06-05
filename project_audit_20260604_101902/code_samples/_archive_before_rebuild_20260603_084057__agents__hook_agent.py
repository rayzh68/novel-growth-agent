from __future__ import annotations

from core.book_loader import BookPackage
from core.llm_client import LLMClient


class HookAgent:
    def __init__(self) -> None:
        self.llm = LLMClient("MODEL_CREATIVE")

    def run(self, book: BookPackage, marketing_profile: dict, personas: dict, selling_points: dict) -> dict:
        fallback = self._fallback(book)
        return self.llm.generate_json(
            "You generate high-performing paid-social hooks for English web novels.",
            f"Book: {book.title}\nMarket: {marketing_profile}\nPersonas: {personas}\nSelling points: {selling_points}",
            fallback,
        )

    def _fallback(self, book: BookPackage) -> dict:
        raw = [
            ("betrayal_hook", "They called her a traitor after she saved them all."),
            ("revenge_hook", "They executed her as a traitor. Ten years later, she returned as their queen."),
            ("hidden_identity_hook", "No one recognized the woman they once condemned to death."),
            ("power_reversal_hook", "The empire that destroyed her now needs her to survive."),
            ("romantic_tension_hook", "He betrayed her once. Now he is the only one who knows she is alive."),
            ("strong_female_lead_hook", "She lost her name, her crown, and her home. She kept her revenge."),
            ("chapter_cliffhanger_hook", "She should have died before sunset. Instead, she woke with a mark no one could explain."),
            ("facebook_primary_hook", "Everyone she trusted betrayed her. Now the empire wants her back."),
            ("tiktok_three_second_hook", "They killed the wrong woman."),
            ("landing_page_hero_hook", "Betrayed by the empire she saved. Reborn as the queen they fear."),
            ("betrayal_hook", "The crowd cheered for her death. They had no idea she would return."),
            ("revenge_hook", "They buried her as a traitor. She came back as their punishment."),
            ("hidden_identity_hook", "At the royal masquerade, her worst enemy recognized her first."),
            ("romantic_tension_hook", "The man who watched her die was the first to find her alive."),
            ("power_reversal_hook", "Once, she begged for mercy. Now kings bargain for her help."),
            ("strong_female_lead_hook", "She learned to survive without trust. Then she returned to take everything back."),
            ("chapter_cliffhanger_hook", "Chapter one ends with a death sentence. Chapter three begins with her return."),
            ("facebook_primary_hook", "If you like revenge, royal secrets, and forbidden tension, start this story tonight."),
            ("tiktok_three_second_hook", "He should have saved her."),
            ("landing_page_hero_hook", "A dark revenge fantasy romance about betrayal, survival, and a crown."),
            ("betrayal_hook", "She saved the kingdom. The kingdom paid her with chains."),
            ("revenge_hook", "The empire wanted a dead traitor. It created a living queen."),
            ("hidden_identity_hook", "She came back under a false name. Only one man saw the truth."),
            ("romantic_tension_hook", "She wanted revenge. He wanted forgiveness. The crown wanted blood."),
            ("power_reversal_hook", "Her enemies built a throne on her grave. Now she is coming for it."),
            ("strong_female_lead_hook", "She did not return for love. She returned for justice."),
            ("chapter_cliffhanger_hook", "The final words of her execution became the first clue to her power."),
            ("facebook_primary_hook", "A betrayed heroine. A dangerous protector. An empire built on lies."),
            ("tiktok_three_second_hook", "Everyone lied about the traitor."),
            ("landing_page_hero_hook", "Start the story of the woman the empire failed to kill.")
        ]
        hooks = []
        for i, (typ, text) in enumerate(raw, start=1):
            score_base = 9 if typ in ["revenge_hook", "betrayal_hook", "tiktok_three_second_hook"] else 8
            hooks.append({
                "hook_id": f"hook_{i:03d}",
                "type": typ,
                "text": text,
                "emotional_score": score_base,
                "clarity_score": 8 if len(text) < 120 else 7,
                "click_potential": score_base,
                "risk_level": "low",
                "recommended_channels": ["facebook", "instagram", "tiktok", "landing_page"] if "tiktok" in typ else ["facebook", "instagram", "landing_page"],
                "matched_personas": ["persona_001", "persona_002"] if i % 2 else ["persona_003", "persona_004"],
                "matched_selling_points": ["sp_001", "sp_002"],
                "hook_appeal_diagnostic": {
                    "hook_appeal": "Strong" if score_base >= 9 else "Medium-strong",
                    "why_it_may_work": "It creates immediate emotional injustice and a clear reason to click.",
                    "improvement_hint": "Test a more specific character or crown visual variant if CTR is low."
                }
            })
        return {"book_id": book.book_id, "hooks": hooks}
