from __future__ import annotations

from core.book_loader import BookPackage
from core.llm_client import LLMClient


class FacebookCreativeAgent:
    def __init__(self) -> None:
        self.llm = LLMClient("MODEL_CREATIVE")

    def run(self, book: BookPackage, marketing_profile: dict, personas: dict, hooks: dict) -> dict:
        fallback = self._fallback(book, marketing_profile, personas, hooks)
        return self.llm.generate_json(
            """
You are a senior growth creative strategist for English serialized fiction.
Generate compliant Facebook/Instagram paid-social ads that can be used for A/B testing.
Do not output generic repeated bodies. Each ad must test a distinct angle.
Return JSON only with this shape:
{
  "book_id": "...",
  "facebook_ads": [
    {
      "ad_id": "fb_ad_001",
      "channel": "facebook",
      "placement": ["facebook_feed", "instagram_feed"],
      "angle_type": "betrayal|revenge|hidden_identity|romantic_tension|power_reversal|strong_heroine|cliffhanger",
      "test_purpose": "what this ad is testing",
      "primary_text": "1-3 short paragraphs",
      "headline": "under 80 chars, not cut mid-word",
      "description": "short line",
      "cta": "Start Reading",
      "hook_id": "hook_001",
      "persona_id": "persona_001",
      "target_persona_note": "who this is for",
      "creative_direction": "visual concept",
      "image_direction": "single image or cover direction",
      "video_direction": "short motion direction if used",
      "appeal_diagnostic": {
        "content_appeal": "...",
        "hook_appeal": "...",
        "creative_appeal": "...",
        "reading_appeal_risk": "...",
        "improvement_hint": "..."
      },
      "risk_level": "low|medium|high",
      "compliance_notes": []
    }
  ]
}
""".strip(),
            f"Book: {book.title}\nMarket: {marketing_profile}\nPersonas: {personas}\nHooks: {hooks}",
            fallback,
        )

    @staticmethod
    def _headline(text: str, max_len: int = 78) -> str:
        text = " ".join(text.split())
        if len(text) <= max_len:
            return text
        cut = text[:max_len].rsplit(" ", 1)[0].rstrip(".,;:!?")
        return cut if cut else text[:max_len].rstrip()

    def _fallback(self, book: BookPackage, marketing_profile: dict, personas: dict, hooks: dict) -> dict:
        hook_list = hooks.get("hooks", [])
        if not hook_list:
            hook_list = [{"hook_id": "hook_001", "text": "They called her a traitor after she saved them all.", "type": "betrayal_hook"}]

        def pick_hook(index: int) -> dict:
            return hook_list[(index - 1) % len(hook_list)]

        # Distinct Facebook/Instagram test angles. These are intentionally not the same body with only a replaced hook.
        ad_specs = [
            {
                "angle_type": "betrayal",
                "persona_id": "persona_001",
                "target_persona_note": "Female-skewed fantasy romance readers who respond to injustice and betrayal.",
                "body_tail": "She saved the kingdom once. They paid her with chains. Now every secret that buried her is about to burn.",
                "description": "A dark fantasy romance of betrayal and return.",
                "creative_direction": "dark royal betrayal, heroine in chains, crowd and throne in the background",
                "image_direction": "cinematic cover: betrayed heroine, torn cloak, palace shadows, red-gold crown light",
                "video_direction": "slow zoom from execution crowd to heroine's calm face, final frame on crown silhouette",
                "test_purpose": "Test whether betrayal/injustice can create low-cost click intent on Facebook Feed.",
            },
            {
                "angle_type": "revenge",
                "persona_id": "persona_001",
                "target_persona_note": "Readers who like revenge arcs, power reversal, and queen energy.",
                "body_tail": "The empire thought her story ended at the execution ground. They were wrong. Her return is not a plea for mercy鈥攊t is the beginning of judgment.",
                "description": "Start a revenge fantasy romance.",
                "creative_direction": "returned queen, dark crown, enemies kneeling, storm-lit throne room",
                "image_direction": "heroine standing before a throne with a broken crown in hand",
                "video_direction": "before/after split: condemned traitor 鈫?feared queen",
                "test_purpose": "Test whether revenge promise improves CTR while still matching chapter-one expectation.",
            },
            {
                "angle_type": "hidden_identity",
                "persona_id": "persona_002",
                "target_persona_note": "Web novel readers who like secrets, disguise, masquerade reveals, and cliffhangers.",
                "body_tail": "She returned under a new name. At the royal masquerade, one man looked at her and realized the dead woman was standing in front of him.",
                "description": "A hidden-identity royal fantasy.",
                "creative_direction": "masquerade ball, masked heroine, dangerous recognition moment",
                "image_direction": "close-up of mask, crown reflection, male lead in background",
                "video_direction": "masked ball text overlays with quick reveal cuts",
                "test_purpose": "Test whether mystery/identity reveal attracts deeper readers instead of curiosity-only clicks.",
            },
            {
                "angle_type": "power_reversal",
                "persona_id": "persona_003",
                "target_persona_note": "Broad female 25-44 audience; clear emotional reversal without heavy fantasy terms.",
                "body_tail": "Once, she begged them to listen. Now the same people who condemned her need her power to survive.",
                "description": "A story about survival, power, and payback.",
                "creative_direction": "before/after transformation, prisoner to powerful royal figure",
                "image_direction": "split visual: chains on left, crown and fire on right",
                "video_direction": "fast transformation edit with bold captions",
                "test_purpose": "Test whether broad power reversal works better than genre-specific fantasy wording.",
            },
            {
                "angle_type": "romantic_tension",
                "persona_id": "persona_001",
                "target_persona_note": "Romantasy readers who respond to betrayal, guilt, and forbidden emotional tension.",
                "body_tail": "He failed her when everyone turned away. Years later, he is the only one who knows the truth鈥攁nd the only one she cannot afford to trust.",
                "description": "Slow-burn tension inside a revenge fantasy.",
                "creative_direction": "two characters separated by palace shadows, guilt and recognition",
                "image_direction": "heroine walking away from a conflicted male lead in a royal corridor",
                "video_direction": "alternating captions: 'He betrayed her' / 'He recognized her first'",
                "test_purpose": "Test whether romance tension improves read depth versus pure revenge hooks.",
            },
            {
                "angle_type": "strong_heroine",
                "persona_id": "persona_003",
                "target_persona_note": "Readers who prefer resilient heroine, justice, and emotional strength.",
                "body_tail": "She lost her name, her home, and every person she trusted. But she did not lose the one thing the empire feared most: her will to return.",
                "description": "Begin her comeback story.",
                "creative_direction": "strong heroine silhouette, storm, palace gate, crown motif",
                "image_direction": "solo heroine walking toward palace gates at night",
                "video_direction": "heroine silhouette plus captions focused on survival and return",
                "test_purpose": "Test whether heroine-strength framing lowers risk of clickbait while keeping emotional pull.",
            },
            {
                "angle_type": "cliffhanger",
                "persona_id": "persona_002",
                "target_persona_note": "Serialized fiction readers who like chapter-end hooks and fast plot movement.",
                "body_tail": "The first chapter ends with a sentence no one can undo. By the third chapter, the empire realizes the execution did not end the threat鈥攊t released it.",
                "description": "Read the opening chapters now.",
                "creative_direction": "chapter preview style, execution sentence, magical mark, cliffhanger CTA",
                "image_direction": "book-page style creative with dramatic text overlay and crown shadow",
                "video_direction": "page-turn animation with three escalating captions",
                "test_purpose": "Test if chapter-preview framing increases Chapter 1 and Chapter 3 finish rates.",
            },
            {
                "angle_type": "betrayal",
                "persona_id": "persona_002",
                "target_persona_note": "Web novel readers who respond to 'everyone betrayed her' openings.",
                "body_tail": "Her closest allies signed the accusation. Her enemies lit the pyre. But the truth they buried with her is about to come back alive.",
                "description": "A serialized revenge fantasy romance.",
                "creative_direction": "signed accusation, burning seal, heroine's return",
                "image_direction": "royal decree burning with heroine silhouette behind smoke",
                "video_direction": "document burn transition into masked heroine reveal",
                "test_purpose": "Test a more story-specific betrayal variant against the broad betrayal hook.",
            },
            {
                "angle_type": "revenge",
                "persona_id": "persona_003",
                "target_persona_note": "Broad audience; simple revenge premise with minimal fantasy vocabulary.",
                "body_tail": "They wanted her erased. Instead, they gave her a reason to come back stronger than every person who betrayed her.",
                "description": "Start reading her return.",
                "creative_direction": "simple emotional revenge creative, less worldbuilding, clear CTA",
                "image_direction": "dramatic portrait with crown-shaped shadow and short overlay text",
                "video_direction": "minimalist text-led creative for broad audience testing",
                "test_purpose": "Test if broad revenge wording beats detailed fantasy positioning on CPC.",
            },
            {
                "angle_type": "hidden_identity",
                "persona_id": "persona_001",
                "target_persona_note": "Romantasy readers who like secret identity plus dangerous recognition.",
                "body_tail": "No one at court knew her face anymore. But one look from the man who once watched her fall told her the most dangerous secret was already exposed.",
                "description": "Secrets, revenge, and forbidden tension.",
                "creative_direction": "court intrigue, close eye contact, secret identity tension",
                "image_direction": "masked heroine facing a man across a candlelit ballroom",
                "video_direction": "romantasy edit with recognition beat at 6 seconds",
                "test_purpose": "Test if identity + romance improves quality of readers from Instagram placements.",
            },
        ]

        ads = []
        for i, spec in enumerate(ad_specs, start=1):
            hook = pick_hook(i)
            hook_text = hook.get("text", "").strip()
            primary_text = f"{hook_text}\n\n{spec['body_tail']}\n\nRead the first chapters now."
            headline = self._headline(hook_text)
            if not headline:
                headline = self._headline(spec["body_tail"])
            ads.append({
                "ad_id": f"fb_ad_{i:03d}",
                "channel": "facebook",
                "placement": ["facebook_feed", "instagram_feed", "instagram_story", "instagram_reels"],
                "angle_type": spec["angle_type"],
                "test_purpose": spec["test_purpose"],
                "primary_text": primary_text,
                "headline": headline,
                "description": spec["description"],
                "cta": "Start Reading",
                "hook_id": hook.get("hook_id", f"hook_{i:03d}"),
                "persona_id": spec["persona_id"],
                "target_persona_note": spec["target_persona_note"],
                "creative_direction": spec["creative_direction"],
                "image_direction": spec["image_direction"],
                "video_direction": spec["video_direction"],
                "appeal_diagnostic": {
                    "content_appeal": "Uses a clear marketable promise: betrayal, comeback, revenge, romance tension, or hidden identity.",
                    "hook_appeal": "Strong opening conflict. Validate with CTR and CPC before scaling.",
                    "creative_appeal": "Visual direction is aligned with the ad angle and target persona.",
                    "reading_appeal_risk": "If the first chapter does not quickly deliver this promise, clicks may not convert into reading depth.",
                    "improvement_hint": "If CTR is weak, rewrite the first sentence. If CTR is strong but Chapter 1 finish is weak, reduce shock language and align the ad closer to chapter content."
                },
                "risk_level": "low",
                "compliance_notes": [
                    "No celebrity/IP comparison.",
                    "No explicit adult claim.",
                    "Avoid claiming events not supported by the manuscript."
                ]
            })
        return {"book_id": book.book_id, "facebook_ads": ads}

