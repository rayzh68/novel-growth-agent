from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class Chapter:
    index: int
    title: str
    text: str
    source_line: int


CN_DIGITS = {
    "\u96f6": 0, "\u3007": 0,
    "\u4e00": 1, "\u4e8c": 2, "\u4e24": 2, "\u4e09": 3, "\u56db": 4, "\u4e94": 5,
    "\u516d": 6, "\u4e03": 7, "\u516b": 8, "\u4e5d": 9,
}

CN_UNITS = {
    "\u5341": 10,
    "\u767e": 100,
    "\u5343": 1000,
    "\u4e07": 10000,
}


def chinese_number_to_int(s: str) -> int | None:
    s = str(s).strip()
    if not s:
        return None
    if s.isdigit():
        return int(s)

    total = 0
    section = 0
    number = 0

    for ch in s:
        if ch in CN_DIGITS:
            number = CN_DIGITS[ch]
        elif ch in CN_UNITS:
            unit = CN_UNITS[ch]
            if unit == 10000:
                section = (section + number) * unit
                total += section
                section = 0
            else:
                if number == 0:
                    number = 1
                section += number * unit
            number = 0
        else:
            return None

    return total + section + number


def split_raw_novel(raw_text: str) -> List[Chapter]:
    lines = raw_text.splitlines()

    # \u7b2c = ?, \u7ae0 = ?
    heading_patterns = [
        re.compile(r"^\s*\u7b2c([0-9\u96f6\u3007\u4e00\u4e8c\u4e24\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u5341\u767e\u5343\u4e07]+)\u7ae0\s*(.*)\s*$"),
        re.compile(r"^\s*Chapter\s*([0-9]+)\s*(.*)\s*$", re.IGNORECASE),
    ]

    starts: List[Dict[str, Any]] = []

    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue

        for pat in heading_patterns:
            m = pat.match(stripped)
            if not m:
                continue

            num_raw = m.group(1)
            idx = int(num_raw) if str(num_raw).isdigit() else chinese_number_to_int(num_raw)
            if idx is None:
                continue

            starts.append({
                "index": idx,
                "title": stripped,
                "line_no": line_no,
            })
            break

    chapters: List[Chapter] = []

    for i, start in enumerate(starts):
        start_line_idx = start["line_no"] - 1
        end_line_idx = starts[i + 1]["line_no"] - 1 if i + 1 < len(starts) else len(lines)
        chunk = "\n".join(lines[start_line_idx:end_line_idx]).strip()

        if chunk:
            chapters.append(Chapter(
                index=int(start["index"]),
                title=str(start["title"]),
                text=chunk,
                source_line=int(start["line_no"]),
            ))

    chapters.sort(key=lambda c: c.index)
    return chapters


def build_chapter_quality_report(chapters: List[Chapter], raw_text: str) -> Dict[str, Any]:
    total = len(chapters)
    report: Dict[str, Any] = {
        "method": "heading",
        "quality": "OK",
        "detected_chapters": total,
        "fallback_used": False,
        "missing_numbers": [],
        "short_chapters": [],
        "avg_chars": 0,
        "min_chars": 0,
        "max_chars": 0,
        "warnings": [],
    }

    if total <= 0:
        report["quality"] = "FALLBACK_CHUNKING"
        report["method"] = "chunk"
        report["fallback_used"] = True
        report["warnings"].append("No chapter headings detected.")
        return report

    indexes = [c.index for c in chapters]
    expected = set(range(min(indexes), max(indexes) + 1))
    missing = sorted(expected - set(indexes))
    report["missing_numbers"] = missing[:50]

    lengths = [len(c.text) for c in chapters]
    avg_len = sum(lengths) / max(1, len(lengths))
    report["avg_chars"] = round(avg_len, 2)
    report["min_chars"] = min(lengths)
    report["max_chars"] = max(lengths)

    short = []
    for ch in chapters:
        if len(ch.text) < max(200, avg_len * 0.2):
            short.append({
                "chapter_index": ch.index,
                "chapter_title": ch.title,
                "chars": len(ch.text),
                "source_line": ch.source_line,
            })

    report["short_chapters"] = short[:50]

    if total < 10:
        report["quality"] = "FALLBACK_CHUNKING"
        report["method"] = "chunk"
        report["fallback_used"] = True
        report["warnings"].append("Too few chapters detected.")
    elif len(missing) > max(5, total * 0.05):
        report["quality"] = "WARN"
        report["warnings"].append("Many missing chapter numbers detected.")
    elif short:
        report["quality"] = "WARN"
        report["warnings"].append("Some chapters are unusually short.")

    return report


def chunk_raw_text(raw_text: str, *, chunk_size: int = 9000) -> List[Chapter]:
    text = raw_text.strip()
    if not text:
        return []

    chunks: List[Chapter] = []
    for i, start in enumerate(range(0, len(text), chunk_size), start=1):
        chunk = text[start:start + chunk_size].strip()
        if chunk:
            chunks.append(Chapter(
                index=i,
                title=f"chunk_{i:03d}",
                text=chunk,
                source_line=0,
            ))
    return chunks


def sample_chapters_for_validation(
    chapters: List[Chapter],
    *,
    front: int = 20,
    mid_each: int = 3,
    end: int = 5,
) -> Dict[str, Any]:
    total = len(chapters)
    selected: Dict[int, Dict[str, Any]] = {}

    def add_range(label: str, start: int, count: int) -> None:
        if total <= 0 or count <= 0:
            return

        start = max(1, min(start, total))
        stop = min(total, start + count - 1)

        for pos in range(start, stop + 1):
            ch = chapters[pos - 1]
            selected[ch.index] = {
                "sample_label": label,
                "chapter_index": ch.index,
                "chapter_title": ch.title,
                "source_line": ch.source_line,
                "text": ch.text,
            }

    add_range("front", 1, front)

    for pct, label in [(0.2, "middle_20pct"), (0.5, "middle_50pct"), (0.8, "middle_80pct")]:
        center = max(1, round(total * pct))
        start = center - max(0, mid_each // 2)
        add_range(label, start, mid_each)

    add_range("ending", max(1, total - end + 1), end)

    ordered = [selected[k] for k in sorted(selected.keys())]

    return {
        "total_chapters": total,
        "selected_count": len(ordered),
        "front": front,
        "mid_each": mid_each,
        "end": end,
        "selected_chapters": ordered,
    }


def load_and_sample_raw_novel(
    raw_path: Path,
    *,
    front: int = 20,
    mid_each: int = 3,
    end: int = 5,
) -> Dict[str, Any]:
    raw_text = raw_path.read_text(encoding="utf-8-sig", errors="ignore")
    chapters = split_raw_novel(raw_text)
    quality_report = build_chapter_quality_report(chapters, raw_text)

    if quality_report.get("fallback_used"):
        chapters = chunk_raw_text(raw_text)
        quality_report = build_chapter_quality_report(chapters, raw_text)
        quality_report["method"] = "chunk"
        quality_report["quality"] = "FALLBACK_CHUNKING"
        quality_report["fallback_used"] = True

    sample = sample_chapters_for_validation(
        chapters,
        front=front,
        mid_each=mid_each,
        end=end,
    )
    sample["raw_path"] = str(raw_path)
    sample["chapter_quality"] = quality_report
    return sample
