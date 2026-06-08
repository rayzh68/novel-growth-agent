from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def _run_module_main(module_name: str, argv: list[str]) -> None:
    """Run an existing internal script through the unified controller.

    The scripts folder is kept as internal implementation modules. Users should
    call this main.py only.
    """
    import importlib

    old_argv = sys.argv[:]
    try:
        sys.argv = [module_name] + argv
        module = importlib.import_module(module_name)
        module.main()
    finally:
        sys.argv = old_argv


def cmd_generate(args: argparse.Namespace) -> None:
    argv = ["--book", args.book]
    if args.input_root:
        argv += ["--input-root", args.input_root]
    if args.output_root:
        argv += ["--output-root", args.output_root]
    _run_module_main("scripts.run_growth_pipeline", argv)


def cmd_analyze(args: argparse.Namespace) -> None:
    argv = ["--book", args.book, "--round", args.round]
    if args.reports_root:
        argv += ["--reports-root", args.reports_root]
    if args.output_root:
        argv += ["--output-root", args.output_root]
    _run_module_main("scripts.run_analysis", argv)


def cmd_all(args: argparse.Namespace) -> None:
    print("=== Step 1/2: Generate promotion assets ===")
    cmd_generate(args)
    print("\n=== Step 2/2: Analyze imported report data ===")
    cmd_analyze(args)
    print("\nDONE. Full workflow finished.")


def cmd_import_book(args: argparse.Namespace) -> None:
    argv = ["--source", args.source, "--book", args.book]
    if args.input_root:
        argv += ["--input-root", args.input_root]
    _run_module_main("scripts.import_book_package", argv)


def cmd_import_report(args: argparse.Namespace) -> None:
    argv = ["--source", args.source, "--type", args.type]
    _run_module_main("scripts.import_ad_report", argv)


def cmd_export_feedback(args: argparse.Namespace) -> None:
    argv = ["--book", args.book, "--target", args.target]
    _run_module_main("scripts.export_feedback", argv)




def cmd_validate(args: argparse.Namespace) -> None:
    from core.commercial_validation import validate_commercial_value
    from core.book_sampling import load_and_sample_raw_novel

    book = args.book
    sample_root = ROOT / "input" / book / "sample_chapters"
    raw_path = ROOT / "input" / book / "raw_novel.txt"

    chapters = []
    sample_meta = {
        "source": None,
        "total_chapters": None,
        "selected_count": None,
        "selected_chapters": [],
    }

    if sample_root.exists():
        files = sorted(sample_root.glob("chapter_*.md")) + sorted(sample_root.glob("chapter_*.txt"))
        for path in files:
            chapters.append(path.read_text(encoding="utf-8-sig", errors="ignore"))
            sample_meta["selected_chapters"].append({
                "sample_label": "manual_sample",
                "chapter_title": path.name,
                "path": str(path),
            })
        if chapters:
            sample_meta["source"] = "sample_chapters"
            sample_meta["selected_count"] = len(chapters)

    if not chapters and raw_path.exists():
        sample = load_and_sample_raw_novel(
            raw_path,
            front=args.front,
            mid_each=args.mid_each,
            end=args.end,
        )
        selected = sample.get("selected_chapters", [])
        chapters = [x.get("text", "") for x in selected if x.get("text")]
        sample_meta = {
            "source": "raw_novel",
            "raw_path": str(raw_path),
            "total_chapters": sample.get("total_chapters"),
            "selected_count": sample.get("selected_count"),
            "front": sample.get("front"),
            "mid_each": sample.get("mid_each"),
            "end": sample.get("end"),
            "chapter_quality": sample.get("chapter_quality"),
            "selected_chapters": [
                {
                    "sample_label": x.get("sample_label"),
                    "chapter_index": x.get("chapter_index"),
                    "chapter_title": x.get("chapter_title"),
                    "source_line": x.get("source_line"),
                }
                for x in selected
            ],
        }

    if not chapters:
        raise SystemExit(
            "No validation input found. Expected either:\n"
            f"- {sample_root}\\chapter_*.md\n"
            f"- {raw_path}"
        )

    result = validate_commercial_value(chapters, book_id=book)
    result["sample"] = sample_meta

    out_dir = ROOT / "output" / "commercial_validation"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{book}_validation.json"

    out_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"OK: saved commercial validation: {out_path}")
    print(json.dumps({
        "book_id": book,
        "source": sample_meta.get("source"),
        "total_chapters": sample_meta.get("total_chapters"),
        "selected_count": sample_meta.get("selected_count"),
        "chapter_quality": (sample_meta.get("chapter_quality") or {}).get("quality"),
        "commercial_promise": result.get("commercial_promise"),
        "creative_potential": result.get("creative_potential"),
        "binge_potential": result.get("binge_potential"),
        "test50_value": result.get("test50_value"),
        "investment_attractiveness": result.get("investment_attractiveness"),
        "recommendation": result.get("recommendation"),
    }, ensure_ascii=False, indent=2))


def cmd_status(args: argparse.Namespace) -> None:
    book = args.book
    checks = [
        ("Input package", ROOT / "input" / book),
        ("Marketing profile", ROOT / "output" / "marketing_profiles" / f"{book}_marketing_profile.json"),
        ("Personas", ROOT / "output" / "personas" / f"{book}_reader_personas.json"),
        ("Selling points", ROOT / "output" / "selling_points" / f"{book}_selling_points.json"),
        ("Hooks", ROOT / "output" / "hooks" / f"{book}_hooks.json"),
        ("Facebook ads", ROOT / "output" / "creatives" / f"{book}_facebook_ads.json"),
        ("TikTok scripts", ROOT / "output" / "creatives" / f"{book}_tiktok_scripts.json"),
        ("Landing spec", ROOT / "output" / "landing_briefs" / f"{book}_landing_page_spec.json"),
        ("UTM links", ROOT / "output" / "utm_links" / f"{book}_utm_links.csv"),
        ("Campaign plan", ROOT / "output" / "campaign_plans" / f"{book}_facebook_campaign_plan.md"),
        ("Growth report", ROOT / "output" / "reports" / f"{book}_growth_report.md"),
        ("Next round plan", ROOT / "output" / "next_rounds" / f"{book}_next_round_plan.md"),
        ("Growth feedback", ROOT / "output" / "feedback" / f"{book}_growth_feedback.json"),
    ]
    print(f"Status for {book}\n")
    for label, path in checks:
        mark = "OK" if path.exists() else "MISSING"
        print(f"[{mark:<7}] {label}: {path}")


def cmd_open(args: argparse.Namespace) -> None:
    """Open the most important output files in VS Code."""
    import subprocess

    book = args.book
    files = [
        ROOT / "output" / "hooks" / f"{book}_hooks.md",
        ROOT / "output" / "creatives" / f"{book}_facebook_ads.md",
        ROOT / "output" / "creatives" / f"{book}_tiktok_scripts.md",
        ROOT / "output" / "landing_briefs" / f"{book}_landing_page_copy.md",
        ROOT / "output" / "campaign_plans" / f"{book}_facebook_campaign_plan.md",
        ROOT / "output" / "reports" / f"{book}_growth_report.md",
        ROOT / "output" / "next_rounds" / f"{book}_next_round_plan.md",
    ]
    existing = [str(x) for x in files if x.exists()]
    missing = [str(x) for x in files if not x.exists()]
    if missing:
        print("Missing files:")
        for x in missing:
            print("-", x)
    if not existing:
        print("No output files found. Run: python main.py all --book", book, "--round round_001")
        return
    try:
        subprocess.run(["code", *existing], check=False)
        print("Opened key output files in VS Code.")
    except FileNotFoundError:
        print("VS Code command 'code' was not found. Open these files manually:")
        for x in existing:
            print("-", x)


def cmd_clean(args: argparse.Namespace) -> None:
    output_root = ROOT / "output"
    if not output_root.exists():
        print("No output folder found.")
        return
    if not args.yes:
        raise SystemExit("Refusing to clean output without --yes")
    for child in output_root.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
            child.mkdir(parents=True, exist_ok=True)
        else:
            child.unlink()
    # Recreate expected output subfolders
    for folder in [
        "marketing_profiles", "personas", "selling_points", "hooks", "creatives",
        "landing_briefs", "utm_links", "campaign_plans", "reports", "next_rounds", "feedback",
    ]:
        (output_root / folder).mkdir(parents=True, exist_ok=True)
    print("Output folder cleaned.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python main.py",
        description="Unified controller for novel-growth-agent. Use this file only; scripts/*.py are internal.",
    )
    sub = parser.add_subparsers(dest="command", required=True)


    p = sub.add_parser("validate", help="Run commercial validation from sample chapters or raw_novel.txt.")
    p.add_argument("--book", default="book_001")
    p.add_argument("--front", type=int, default=20)
    p.add_argument("--mid-each", type=int, default=3)
    p.add_argument("--end", type=int, default=5)
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("generate", help="Generate marketing assets, creatives, landing brief, UTM links, and campaign plan.")
    p.add_argument("--book", default="book_001")
    p.add_argument("--input-root", default=None)
    p.add_argument("--output-root", default=None)
    p.set_defaults(func=cmd_generate)

    p = sub.add_parser("analyze", help="Analyze imported ad/site CSV reports and generate growth report, next round plan, feedback.")
    p.add_argument("--book", default="book_001")
    p.add_argument("--round", default="round_001")
    p.add_argument("--reports-root", default=None)
    p.add_argument("--output-root", default=None)
    p.set_defaults(func=cmd_analyze)

    p = sub.add_parser("all", help="Run generate + analyze in one command.")
    p.add_argument("--book", default="book_001")
    p.add_argument("--round", default="round_001")
    p.add_argument("--input-root", default=None)
    p.add_argument("--output-root", default=None)
    p.add_argument("--reports-root", default=None)
    p.set_defaults(func=cmd_all)

    p = sub.add_parser("import-book", help="Import a marketing package from novel-mvp into input/<book>.")
    p.add_argument("--source", required=True)
    p.add_argument("--book", required=True)
    p.add_argument("--input-root", default=None)
    p.set_defaults(func=cmd_import_book)

    p = sub.add_parser("import-report", help="Import one CSV report into data_reports/ad_reports or data_reports/site_events.")
    p.add_argument("--source", required=True)
    p.add_argument("--type", choices=["ad", "site"], required=True)
    p.set_defaults(func=cmd_import_report)

    p = sub.add_parser("export-feedback", help="Export growth_feedback.json to another system folder.")
    p.add_argument("--book", default="book_001")
    p.add_argument("--target", required=True)
    p.set_defaults(func=cmd_export_feedback)

    p = sub.add_parser("open", help="Open key output Markdown files in VS Code.")
    p.add_argument("--book", default="book_001")
    p.set_defaults(func=cmd_open)

    p = sub.add_parser("status", help="Show whether key input/output files exist for a book.")
    p.add_argument("--book", default="book_001")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("clean", help="Clean output folder. Requires --yes.")
    p.add_argument("--yes", action="store_true")
    p.set_defaults(func=cmd_clean)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

