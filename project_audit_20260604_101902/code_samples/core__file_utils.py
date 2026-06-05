from __future__ import annotations

import json
import csv
from pathlib import Path
from typing import Any, Dict, Iterable, List


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_text(path: Path, default: str = "") -> str:
    if not path.exists():
        return default
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str] | None = None) -> None:
    ensure_dir(path.parent)
    if not rows:
        fieldnames = fieldnames or []
    else:
        fieldnames = fieldnames or list(rows[0].keys())
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def slugify(value: str) -> str:
    import re
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "item"


# --- BOM-safe read_json override ---
def read_json(path, default=None):
    import json as _json
    from pathlib import Path as _Path

    p = _Path(path)
    if not p.exists():
        return {} if default is None else default

    try:
        with p.open("r", encoding="utf-8-sig") as f:
            return _json.load(f)
    except Exception:
        if default is not None:
            return default
        raise
