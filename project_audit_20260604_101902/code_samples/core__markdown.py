from __future__ import annotations

from typing import Any, Dict, Iterable, List


def bullets(items: Iterable[Any]) -> str:
    return "\n".join(f"- {item}" for item in items)


def table(rows: List[Dict[str, Any]], columns: List[str]) -> str:
    if not rows:
        return ""
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = []
    for row in rows:
        body.append("| " + " | ".join(str(row.get(c, "")) for c in columns) + " |")
    return "\n".join([header, sep] + body)
