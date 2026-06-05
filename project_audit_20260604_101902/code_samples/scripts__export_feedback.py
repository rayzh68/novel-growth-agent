from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", default="book_001")
    parser.add_argument("--target", required=True, help="Target folder, e.g. D:\\novel-mvp\\input\\growth_feedback")
    args = parser.parse_args()

    source = ROOT / "output" / "feedback" / f"{args.book}_growth_feedback.json"
    if not source.exists():
        raise FileNotFoundError(f"Feedback file not found: {source}")

    target_folder = Path(args.target)
    target_folder.mkdir(parents=True, exist_ok=True)
    target = target_folder / source.name
    shutil.copy2(source, target)
    print(f"Exported {source} -> {target}")


if __name__ == "__main__":
    main()
