from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv


class LLMClient:
    """
    OpenRouter wrapper with safe fallback.

    V1 can run in MOCK_LLM=1 mode. This keeps the project runnable before
    you configure an API key.
    """

    def __init__(self, model_env: str = "MODEL_DEFAULT") -> None:
        load_dotenv()
        self.api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        self.base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip()
        self.model = os.getenv(model_env, "") or os.getenv("MODEL_DEFAULT", "openai/gpt-4o-mini")
        self.mock = os.getenv("MOCK_LLM", "1").strip() == "1"

    def generate_json(self, system_prompt: str, user_prompt: str, fallback: Any) -> Any:
        if self.mock or not self.api_key:
            return fallback
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt + "\n\nReturn valid JSON only."},
                ],
                temperature=0.7,
            )
            content = response.choices[0].message.content or ""
            return self._parse_json(content, fallback)
        except Exception as exc:
            print(f"[LLM fallback] {exc}")
            return fallback

    @staticmethod
    def _parse_json(content: str, fallback: Any) -> Any:
        content = content.strip()
        if content.startswith("```"):
            content = content.strip("`")
            content = content.replace("json\n", "", 1).replace("JSON\n", "", 1)
        try:
            return json.loads(content)
        except Exception:
            start = content.find("{")
            end = content.rfind("}")
            if start >= 0 and end > start:
                try:
                    return json.loads(content[start:end + 1])
                except Exception:
                    pass
            start = content.find("[")
            end = content.rfind("]")
            if start >= 0 and end > start:
                try:
                    return json.loads(content[start:end + 1])
                except Exception:
                    pass
        return fallback
