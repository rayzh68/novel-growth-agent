import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List

import requests

from research.schema import ResearchItem, ResearchResult


def _mock_search(query: str, limit: int) -> ResearchResult:
    items = [
        ResearchItem(
            provider="facebook",
            query=query,
            title=f"[MOCK] Facebook ad angle for {query}",
            snippet="She was betrayed, abandoned, and underestimated. Now she returns stronger than ever.",
            url="",
            meta={
                "cta": "Read Now",
                "source_type": "mock_ad",
                "angle": "betrayal_revenge",
            },
        )
    ]
    return ResearchResult(provider="facebook", query=query, items=items[:limit])


def _manual_json_search(query: str, limit: int) -> ResearchResult:
    path = Path(os.getenv("FACEBOOK_MANUAL_JSON", "data/facebook_manual_ads.json"))
    if not path.exists():
        raise FileNotFoundError(f"FACEBOOK_MANUAL_JSON not found: {path}")

    raw = json.loads(path.read_text(encoding="utf-8"))
    rows = raw if isinstance(raw, list) else raw.get("items", [])

    items: List[ResearchItem] = []
    q = query.lower()

    for row in rows:
        text = " ".join([
            str(row.get("title", "")),
            str(row.get("body", "")),
            str(row.get("snippet", "")),
            str(row.get("angle", "")),
        ]).lower()

        if q not in text and not any(x in text for x in q.split()):
            continue

        items.append(
            ResearchItem(
                provider="facebook",
                query=query,
                title=str(row.get("title", "")),
                snippet=str(row.get("body") or row.get("snippet") or ""),
                url=str(row.get("url", "")),
                meta={
                    "cta": row.get("cta", ""),
                    "source_type": "manual_json",
                    "angle": row.get("angle", ""),
                    "raw": row,
                },
            )
        )

        if len(items) >= limit:
            break

    return ResearchResult(provider="facebook", query=query, items=items)


def _apify_search(query: str, limit: int) -> ResearchResult:
    token = os.getenv("APIFY_TOKEN", "").strip()
    actor_id = os.getenv("FACEBOOK_APIFY_ACTOR_ID", "").strip()

    if not token:
        raise RuntimeError("Missing APIFY_TOKEN in .env")
    if not actor_id:
        raise RuntimeError("Missing FACEBOOK_APIFY_ACTOR_ID in .env")

    run_url = f"https://api.apify.com/v2/acts/{actor_id}/runs?token={token}"

    payload: Dict[str, Any] = {
        "query": query,
        "searchQuery": query,
        "maxItems": limit,
        "limit": limit,
    }

    r = requests.post(run_url, json=payload, timeout=60)
    r.raise_for_status()
    run = r.json()["data"]
    run_id = run["id"]

    status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={token}"

    for _ in range(60):
        s = requests.get(status_url, timeout=30)
        s.raise_for_status()
        data = s.json()["data"]
        status = data.get("status")

        if status == "SUCCEEDED":
            dataset_id = data["defaultDatasetId"]
            items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={token}&clean=true"
            d = requests.get(items_url, timeout=60)
            d.raise_for_status()
            rows = d.json()
            break

        if status in {"FAILED", "ABORTED", "TIMED-OUT"}:
            raise RuntimeError(f"Apify run failed: {status}")

        time.sleep(5)
    else:
        raise TimeoutError("Apify run polling timeout")

    items: List[ResearchItem] = []

    for row in rows[:limit]:
        title = str(row.get("title") or row.get("headline") or row.get("pageName") or "")
        body = str(row.get("body") or row.get("text") or row.get("adText") or row.get("description") or "")
        url = str(row.get("url") or row.get("adUrl") or row.get("landingPageUrl") or "")

        items.append(
            ResearchItem(
                provider="facebook",
                query=query,
                title=title,
                snippet=body,
                url=url,
                meta={
                    "cta": row.get("cta") or row.get("callToAction") or "",
                    "source_type": "apify",
                    "raw": row,
                },
            )
        )

    return ResearchResult(provider="facebook", query=query, items=items)


def search(query: str, limit: int = 10) -> ResearchResult:
    mode = os.getenv("FACEBOOK_PROVIDER_MODE", "mock").strip().lower()

    if mode == "mock":
        return _mock_search(query, limit)

    if mode == "manual_json":
        return _manual_json_search(query, limit)

    if mode == "apify":
        return _apify_search(query, limit)

    raise ValueError(f"Unknown FACEBOOK_PROVIDER_MODE: {mode}")
