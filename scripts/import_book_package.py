from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Source marketing package folder, e.g. D:\\novel-mvp\\output\\marketing_package\\book_001")
    parser.add_argument("--book", required=True, help="Target book id, e.g. book_001")
    parser.add_argument("--input-root", default=str(ROOT / "input"))
    args = parser.parse_args()

    source = Path(args.source)
    target = Path(args.input_root) / args.book

    if not source.exists():
        raise FileNotFoundError(source)

    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(source, target)
    print(f"Imported {source} -> {target}")


if __name__ == "__main__":
    main()
