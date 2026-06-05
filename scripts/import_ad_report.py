from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="CSV file path")
    parser.add_argument("--type", choices=["ad", "site"], required=True)
    args = parser.parse_args()

    source = Path(args.source)
    if not source.exists():
        raise FileNotFoundError(source)

    folder = ROOT / "data_reports" / ("ad_reports" if args.type == "ad" else "site_events")
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / source.name
    shutil.copy2(source, target)
    print(f"Imported {source} -> {target}")


if __name__ == "__main__":
    main()
