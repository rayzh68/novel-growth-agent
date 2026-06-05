import tempfile
import os
import argparse
import importlib
import json
from datetime import datetime
from pathlib import Path


PROVIDERS = {
    "facebook": "research.providers.facebook",
    "google": "research.providers.google",
    "reddit": "research.providers.reddit",
}


def run_provider(provider: str, query: str, limit: int):
    if provider not in PROVIDERS:
        raise ValueError(f"Unknown provider: {provider}. Available: {', '.join(PROVIDERS)}")

    module = importlib.import_module(PROVIDERS[provider])
    return module.search(query=query, limit=limit)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--providers", default="facebook,google,reddit")
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--book", default="book_test")
    args = parser.parse_args()

    selected = [x.strip() for x in args.providers.split(",") if x.strip()]

    payload = {
        "book": args.book,
        "query": args.query,
        "providers": selected,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "results": [],
    }

    for provider in selected:
        result = run_provider(provider, args.query, args.limit)
        payload["results"].append(result.to_dict())

    out_dir = Path(os.environ.get("NOVEL_GROWTH_SINGLE_RAW_DIR", str(Path(tempfile.gettempdir()) / "novel-growth-agent" / "research_raw_tmp")))
    out_dir.mkdir(parents=True, exist_ok=True)

    safe_query = "".join(c if c.isalnum() else "_" for c in args.query.lower()).strip("_")
    out = out_dir / f"{args.book}_{safe_query}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"OK: saved {out}")


if __name__ == "__main__":
    main()
