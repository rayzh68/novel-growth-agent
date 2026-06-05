import os
import tempfile
import shutil
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

def _cleanup_per_query_raw_files(book: str) -> None:
    """Keep only one raw research file per book.

    Required project rule:
    output/research/raw/{book}_raw_research.json is the only raw file kept.
    Per-query raw files are implementation leakage and must not remain.
    """
    raw_dir = Path(__file__).resolve().parents[1] / "output" / "research" / "raw"
    keep_name = f"{book}_raw_research.json"

    if not raw_dir.exists():
        return

    for item in raw_dir.glob(f"{book}_*.json"):
        if item.name == keep_name:
            continue
        try:
            item.unlink()
        except FileNotFoundError:
            pass



def run_one(book, query, providers, limit):
    cmd = [
        sys.executable,
        "-m",
        "research.runner",
        "--providers",
        providers,
        "--query",
        query,
        "--limit",
        limit,
        "--book",
        book,
    ]
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", required=True)
    parser.add_argument("--config", default="config/research_queries.json")
    parser.add_argument("--max-queries", type=int, default=0)
    args = parser.parse_args()

    profile_path = Path(f"output/market_profiles/{args.book}_market_profile.json")

    if profile_path.exists():
        profile = json.loads(profile_path.read_text(encoding="utf-8-sig"))
        plan = profile.get("research_query_plan", [])
        if plan:
            queries = [
                x.get("query", "")
                for x in sorted(plan, key=lambda y: y.get("priority", 0), reverse=True)
                if x.get("query")
            ]
        else:
            queries = profile.get("research_queries", [])

        providers = ",".join(profile.get("research_providers", ["facebook", "google", "reddit"]))
        limit = str(profile.get("limit_per_query", 10))
        print(f"Using market profile queries: {profile_path}")
    else:
        cfg_path = Path(args.config)
        data = json.loads(cfg_path.read_text(encoding="utf-8-sig"))
        if args.book not in data:
            raise SystemExit(f"Book not found in config and no market profile found: {args.book}")

        book_cfg = data[args.book]
        queries = book_cfg.get("queries", [])
        providers = ",".join(book_cfg.get("providers", ["facebook", "google", "reddit"]))
        limit = str(book_cfg.get("limit_per_query", 10))
        print(f"Using fallback config queries: {cfg_path}")

    if args.max_queries and args.max_queries > 0:
        queries = queries[:args.max_queries]
        print(f"Limited research queries to first {args.max_queries}")

    final_raw_dir = Path("output/research/raw")
    final_raw_dir.mkdir(parents=True, exist_ok=True)

    raw_dir = Path(tempfile.gettempdir()) / "novel-growth-agent" / "research_raw_tmp" / args.book
    if raw_dir.exists():
        shutil.rmtree(raw_dir, ignore_errors=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    os.environ["NOVEL_GROWTH_SINGLE_RAW_DIR"] = str(raw_dir)

    combined = {
        "book": args.book,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "providers": providers.split(","),
        "limit_per_query": int(limit),
        "queries": queries,
        "results": []
    }

    for query in queries:
        print("=" * 80)
        print(f"RUN RESEARCH | book={args.book} | query={query} | providers={providers}")
        print("=" * 80)

        run_one(args.book, query, providers, limit)

        safe_query = "".join(c if c.isalnum() else "_" for c in query.lower()).strip("_")
        single_path = raw_dir / f"{args.book}_{safe_query}.json"

        if single_path.exists():
            payload = json.loads(single_path.read_text(encoding="utf-8-sig"))
            combined["results"].append(payload)
            single_path.unlink()

    out = final_raw_dir / f"{args.book}_raw_research.json"
    out.write_text(json.dumps(combined, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: saved combined raw research: {out}")
    _cleanup_per_query_raw_files(args.book)
    shutil.rmtree(raw_dir, ignore_errors=True)
    os.environ.pop("NOVEL_GROWTH_SINGLE_RAW_DIR", None)


if __name__ == "__main__":
    main()
