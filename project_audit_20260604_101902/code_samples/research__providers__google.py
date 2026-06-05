import json
import os
from pathlib import Path
from typing import List

import requests
from dotenv import load_dotenv

from research.schema import ResearchItem, ResearchResult

load_dotenv()


def _mock_search(query: str, limit: int) -> ResearchResult:
    items = [
        ResearchItem(
            provider="google",
            query=query,
            title=f"[MOCK] Google search result for {query}",
            snippet="Mock Google result: related searches, SEO pages, and competitor content will appear here.",
            url="",
            meta={
                "source_type": "mock_search",
                "related_queries": [
                    f"best {query} books",
                    f"{query} recommendations",
                    f"{query} novels",
                ],
            },
        )
    ]
    return ResearchResult(provider="google", query=query, items=items[:limit])


def _manual_json_search(query: str, limit: int) -> ResearchResult:
    path = Path(os.getenv("GOOGLE_MANUAL_JSON", "data/google_manual_results.json"))
    if not path.exists():
        raise FileNotFoundError(f"GOOGLE_MANUAL_JSON not found: {path}")

    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    rows = raw if isinstance(raw, list) else raw.get("items", [])

    items: List[ResearchItem] = []
    q = query.lower()

    for row in rows:
        text = " ".join([
            str(row.get("title", "")),
            str(row.get("snippet", "")),
            str(row.get("url", "")),
        ]).lower()

        if q not in text and not any(x in text for x in q.split()):
            continue

        items.append(
            ResearchItem(
                provider="google",
                query=query,
                title=str(row.get("title", "")),
                snippet=str(row.get("snippet", "")),
                url=str(row.get("url", "")),
                meta={
                    "source_type": "manual_json",
                    "related_queries": row.get("related_queries", []),
                    "people_also_ask": row.get("people_also_ask", []),
                    "raw": row,
                },
            )
        )

        if len(items) >= limit:
            break

    return ResearchResult(provider="google", query=query, items=items)


def _tavily_search(query: str, limit: int) -> ResearchResult:
    api_key = os.getenv("TAVILY_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Missing TAVILY_API_KEY in .env")

    payload = {
        "query": query,
        "search_depth": os.getenv("TAVILY_SEARCH_DEPTH", "basic"),
        "max_results": limit,
        "include_answer": False,
        "include_raw_content": False,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    r = requests.post(
        "https://api.tavily.com/search",
        headers=headers,
        json=payload,
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()

    rows = data.get("results", [])
    items: List[ResearchItem] = []

    for row in rows[:limit]:
        items.append(
            ResearchItem(
                provider="google",
                query=query,
                title=str(row.get("title", "")),
                snippet=str(row.get("content", "")),
                url=str(row.get("url", "")),
                meta={
                    "source_type": "tavily_search",
                    "score": row.get("score"),
                    "raw": row,
                },
            )
        )

    return ResearchResult(provider="google", query=query, items=items)


def search(query: str, limit: int = 10) -> ResearchResult:
    mode = os.getenv("GOOGLE_PROVIDER_MODE", "mock").strip().lower()

    if mode == "mock":
        return _mock_search(query, limit)

    if mode == "manual_json":
        return _manual_json_search(query, limit)

    if mode == "tavily":
        return _tavily_search(query, limit)

    raise ValueError(f"Unknown GOOGLE_PROVIDER_MODE: {mode}")
