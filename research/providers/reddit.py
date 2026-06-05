import json
import os
from pathlib import Path
from typing import List

from research.schema import ResearchItem, ResearchResult


def _mock_search(query: str, limit: int) -> ResearchResult:
    items = [
        ResearchItem(
            provider="reddit",
            query=query,
            title=f"[MOCK] Reddit reader discussion for {query}",
            snippet="Mock Reddit discussion: readers mention what they love, hate, recommend, and abandon.",
            url="",
            meta={
                "source_type": "mock_discussion",
                "subreddit": "RomanceBooks",
                "score": 123,
                "top_comments": [
                    "I love revenge arcs when the heroine actually wins.",
                    "Strong female leads work best when the emotional stakes are clear.",
                ],
            },
        )
    ]
    return ResearchResult(provider="reddit", query=query, items=items[:limit])


def _manual_json_search(query: str, limit: int) -> ResearchResult:
    path = Path(os.getenv("REDDIT_MANUAL_JSON", "data/reddit_manual_threads.json"))
    if not path.exists():
        raise FileNotFoundError(f"REDDIT_MANUAL_JSON not found: {path}")

    raw = json.loads(path.read_text(encoding="utf-8"))
    rows = raw if isinstance(raw, list) else raw.get("items", [])

    items: List[ResearchItem] = []
    q = query.lower()

    for row in rows:
        text = " ".join([
            str(row.get("title", "")),
            str(row.get("snippet", "")),
            " ".join(map(str, row.get("top_comments", []))),
        ]).lower()

        if q not in text and not any(x in text for x in q.split()):
            continue

        items.append(
            ResearchItem(
                provider="reddit",
                query=query,
                title=str(row.get("title", "")),
                snippet=str(row.get("snippet", "")),
                url=str(row.get("url", "")),
                meta={
                    "source_type": "manual_json",
                    "subreddit": row.get("subreddit", ""),
                    "score": row.get("score", 0),
                    "top_comments": row.get("top_comments", []),
                    "raw": row,
                },
            )
        )

        if len(items) >= limit:
            break

    return ResearchResult(provider="reddit", query=query, items=items)


def search(query: str, limit: int = 10) -> ResearchResult:
    mode = os.getenv("REDDIT_PROVIDER_MODE", "mock").strip().lower()

    if mode == "mock":
        return _mock_search(query, limit)

    if mode == "manual_json":
        return _manual_json_search(query, limit)

    raise ValueError(f"Unknown REDDIT_PROVIDER_MODE: {mode}")
