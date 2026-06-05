import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def make_key(item: Dict[str, Any]) -> str:
    provider = str(item.get("provider", "")).strip().lower()
    title = str(item.get("title", "")).strip().lower()
    snippet = str(item.get("snippet", "")).strip().lower()
    url = str(item.get("url", "")).strip().lower()
    base = url or f"{provider}|{title}|{snippet[:160]}"
    return hashlib.md5(base.encode("utf-8", errors="ignore")).hexdigest()


def normalize_item(item: Dict[str, Any], source_file: str) -> Dict[str, Any]:
    return {
        "provider": str(item.get("provider", "")).strip(),
        "query": str(item.get("query", "")).strip(),
        "title": str(item.get("title", "")).strip(),
        "snippet": str(item.get("snippet", "")).strip(),
        "url": str(item.get("url", "")).strip(),
        "meta": item.get("meta", {}) if isinstance(item.get("meta", {}), dict) else {},
        "source_file": source_file,
    }


def iter_results_from_payload(payload: Dict[str, Any]):
    # New format:
    # {
    #   "results": [
    #      { "book":..., "query":..., "results": [provider_result...] },
    #      ...
    #   ]
    # }
    for entry in payload.get("results", []):
        if isinstance(entry, dict) and isinstance(entry.get("results"), list):
            for provider_result in entry.get("results", []):
                yield provider_result
        elif isinstance(entry, dict) and isinstance(entry.get("items"), list):
            yield entry


def clean_research(book: str, raw_dir: Path, out_dir: Path) -> Path:
    combined_raw = raw_dir / f"{book}_raw_research.json"

    if combined_raw.exists():
        files = [combined_raw]
    else:
        files = sorted(raw_dir.glob(f"{book}_*.json"))

    if not files:
        raise SystemExit(f"No raw files found for book={book} in {raw_dir}")

    seen = set()
    by_provider: Dict[str, List[Dict[str, Any]]] = {}
    all_items: List[Dict[str, Any]] = []

    for file in files:
        payload = load_json(file)

        for result in iter_results_from_payload(payload):
            provider = str(result.get("provider", "")).strip() or "unknown"
            items = result.get("items", [])

            for item in items:
                norm = normalize_item(item, file.name)
                key = make_key(norm)

                if key in seen:
                    continue

                seen.add(key)
                all_items.append(norm)
                by_provider.setdefault(provider, []).append(norm)

    output = {
        "book": book,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "source_raw_files": [x.name for x in files],
        "stats": {
            "raw_files": len(files),
            "unique_items": len(all_items),
            "providers": {
                provider: len(items)
                for provider, items in sorted(by_provider.items())
            },
        },
        "by_provider": by_provider,
        "items": all_items,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{book}_market_research_clean.json"
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    return out_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", required=True)
    parser.add_argument("--raw-dir", default="output/research/raw")
    parser.add_argument("--out-dir", default="output/research/clean")
    args = parser.parse_args()

    out = clean_research(
        book=args.book,
        raw_dir=Path(args.raw_dir),
        out_dir=Path(args.out_dir),
    )

    print(f"OK: saved {out}")


if __name__ == "__main__":
    main()
