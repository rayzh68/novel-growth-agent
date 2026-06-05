import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[1]


GENERIC_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "being", "but", "by",
    "can", "could", "did", "do", "does", "doing", "for", "from", "had", "has",
    "have", "having", "he", "her", "hers", "him", "his", "i", "if", "in",
    "into", "is", "it", "its", "me", "more", "most", "my", "no", "not",
    "of", "on", "or", "our", "out", "over", "she", "so", "some", "such",
    "than", "that", "the", "their", "them", "then", "there", "these",
    "they", "this", "those", "to", "too", "up", "very", "was", "we",
    "were", "what", "when", "where", "which", "who", "why", "will",
    "with", "would", "you", "your", "about", "after", "also", "because",
    "before", "between", "how", "just", "like", "may", "new", "now",
    "one", "only", "other", "same", "through", "use", "used", "using",
    "via", "while", "within", "without"
}

MARKET_PATTERN_NOISE_TOKENS = {
    # provider / mock / query wrapper noise, not genre taxonomy
    "mock", "test", "sample", "example", "placeholder", "template",
    "facebook", "reddit", "google", "provider", "providers",
    "platform", "platforms", "search", "query", "queries",
    "result", "results", "snippet", "snippets",

    # ad/test prompt wrappers
    "ad", "ads", "angle", "angles", "campaign", "campaigns",
    "creative", "creatives", "copy", "cta",

    # generic wrappers from our generated research queries
    "reader", "readers", "discussion", "discussions",
    "audience", "audiences", "web", "online", "fiction",
    "novel", "novels", "book", "books", "club",

    # technical contamination
    "legacy", "variant", "variants", "raw", "extraction",
    "obsolete", "mojibake", "encoding", "encoded", "decode",
    "decoded", "garbled", "charset", "utf", "utf8", "utf-8",
    "latin", "ascii", "chinese", "character", "characters",
    "chinese-character", "source-language"
}



TEXT_FIELDS = {
    "title",
    "headline",
    "snippet",
    "description",
    "summary",
    "subhead",
    "caption",
    "meta",
    "metadata",
    "content",
    "body",
    "text",
    "page_text",
    "article",
}


SOURCE_FIELDS = {
    "url",
    "link",
    "source",
    "domain",
    "site",
    "publisher",
}


QUERY_FIELDS = {
    "query",
    "search_query",
    "research_query",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> Any:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def compact_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return " ".join(compact_text(v) for v in value if v is not None)
    if isinstance(value, dict):
        parts = []
        for k, v in value.items():
            key = str(k).lower()
            if key in TEXT_FIELDS:
                parts.append(compact_text(v))
            elif isinstance(v, (dict, list)):
                parts.append(compact_text(v))
        return " ".join(p for p in parts if p)
    return ""


def first_text(item: Dict[str, Any], keys: Iterable[str]) -> str:
    for key in keys:
        if key in item:
            text = compact_text(item.get(key))
            if text:
                return text
    return ""


def collect_text_parts(item: Dict[str, Any]) -> Dict[str, str]:
    title = first_text(item, ["title", "headline"])
    snippet = first_text(item, ["snippet", "description", "summary", "subhead", "caption"])
    meta = first_text(item, ["meta", "metadata"])
    content = first_text(item, ["content", "body", "text", "page_text", "article"])
    fallback = compact_text(item)

    return {
        "title": title,
        "snippet": snippet,
        "meta": meta,
        "content": content,
        "fallback": fallback,
    }


def collect_source(item: Dict[str, Any]) -> Dict[str, str]:
    result = {}
    for key in SOURCE_FIELDS:
        if key in item:
            value = compact_text(item.get(key))
            if value:
                result[key] = value
    return result


def collect_query(item: Dict[str, Any]) -> str:
    return first_text(item, QUERY_FIELDS)


def looks_like_result(item: Dict[str, Any]) -> bool:
    keys = {str(k).lower() for k in item.keys()}
    has_text = bool(keys & TEXT_FIELDS)
    has_source = bool(keys & SOURCE_FIELDS)
    has_query = bool(keys & QUERY_FIELDS)
    return has_text and (has_source or has_query or "title" in keys or "snippet" in keys)


def flatten_result_items(data: Any) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []

    def walk(node: Any, inherited_query: str = "") -> None:
        if isinstance(node, dict):
            current_query = inherited_query or collect_query(node)

            if looks_like_result(node):
                copied = dict(node)
                if current_query and not collect_query(copied):
                    copied["_inherited_query"] = current_query
                items.append(copied)

            for value in node.values():
                if isinstance(value, (dict, list)):
                    walk(value, current_query)

        elif isinstance(node, list):
            for value in node:
                walk(value, inherited_query)

    walk(data)

    deduped = []
    seen = set()

    for item in items:
        parts = collect_text_parts(item)
        source = collect_source(item)
        identity = (
            source.get("url")
            or source.get("link")
            or (parts["title"] + " " + parts["snippet"])[:240]
        )
        identity = identity.strip().lower()

        if not identity or identity in seen:
            continue

        seen.add(identity)
        deduped.append(item)

    return deduped


def tokenize(text: str) -> List[str]:
    text = text.lower()
    raw = re.findall(r"[a-z][a-z'\-]{1,}|[\u4e00-\u9fff]{2,}", text)
    tokens = []

    for token in raw:
        token = token.strip("-'")
        if not token:
            continue
        if token in GENERIC_STOPWORDS:
            continue
        if len(token) < 2:
            continue
        tokens.append(token)

    return tokens


def valid_phrase(phrase: str) -> bool:
    if not phrase:
        return False
    if "http" in phrase or "www" in phrase:
        return False
    if re.fullmatch(r"[\d\W_]+", phrase):
        return False

    words = phrase.split()

    if len(words) < 2 or len(words) > 4:
        return False
    if all(w in GENERIC_STOPWORDS for w in words):
        return False
    if len(set(words)) == 1:
        return False

    return True


def extract_phrases_from_text(text: str, min_n: int = 2, max_n: int = 4) -> Counter:
    tokens = tokenize(text)
    counter: Counter = Counter()

    for n in range(min_n, max_n + 1):
        if len(tokens) < n:
            continue

        for i in range(0, len(tokens) - n + 1):
            phrase = " ".join(tokens[i:i + n])
            if valid_phrase(phrase):
                counter[phrase] += 1

    return counter


def noisy_market_pattern(phrase: str) -> bool:
    phrase = " ".join(tokenize(phrase))
    if not phrase:
        return True

    words = phrase.split()

    if len(words) < 2:
        return True

    if any(w in MARKET_PATTERN_NOISE_TOKENS for w in words):
        return True

    if any("-" in w and any(part in MARKET_PATTERN_NOISE_TOKENS for part in w.split("-")) for w in words):
        return True

    strong = [
        w for w in words
        if w not in GENERIC_STOPWORDS and w not in MARKET_PATTERN_NOISE_TOKENS
    ]

    if len(strong) < 2:
        return True

    return False


def build_market_patterns(items: List[Dict[str, Any]], limit: int = 40) -> List[Dict[str, Any]]:
    phrase_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "occurrence_count": 0,
        "result_keys": set(),
        "title_hits": 0,
        "snippet_hits": 0,
        "meta_hits": 0,
        "content_hits": 0,
        "queries": Counter(),
        "evidence": [],
    })

    for idx, item in enumerate(items):
        parts = collect_text_parts(item)
        source = collect_source(item)
        query = collect_query(item) or compact_text(item.get("_inherited_query"))

        weighted_sections: List[Tuple[str, str, int]] = [
            ("title", parts["title"], 4),
            ("snippet", parts["snippet"], 3),
            ("meta", parts["meta"], 2),
            ("content", parts["content"], 1),
        ]

        if not any(text for _, text, _ in weighted_sections):
            weighted_sections = [("content", parts["fallback"], 1)]

        result_key = (
            source.get("url")
            or source.get("link")
            or (parts["title"] + " " + parts["snippet"])[:240]
            or str(idx)
        )

        local_seen = set()

        for section_name, section_text, weight in weighted_sections:
            if not section_text:
                continue

            phrase_counts = extract_phrases_from_text(section_text)

            for phrase, count in phrase_counts.items():
                stats = phrase_stats[phrase]
                stats["occurrence_count"] += count * weight
                stats["result_keys"].add(result_key)
                stats[f"{section_name}_hits"] += count

                if query:
                    stats["queries"][query] += 1

                if phrase not in local_seen and len(stats["evidence"]) < 5:
                    stats["evidence"].append({
                        "title": parts["title"],
                        "snippet": parts["snippet"][:500],
                        "url": source.get("url") or source.get("link") or "",
                        "source": source.get("source") or source.get("domain") or source.get("site") or "",
                        "query": query,
                    })
                    local_seen.add(phrase)

    patterns = []

    for phrase, stats in phrase_stats.items():
        result_count = len(stats["result_keys"])
        occurrence_count = int(stats["occurrence_count"])

        if noisy_market_pattern(phrase):
            continue

        if result_count < 2 and occurrence_count < 6:
            continue

        score = (
            result_count * 5
            + occurrence_count
            + stats["title_hits"] * 4
            + stats["snippet_hits"] * 3
            + stats["meta_hits"] * 2
        )

        matched_queries = [q for q, _ in stats["queries"].most_common(8)]

        patterns.append({
            "pattern": phrase,
            "phrase": phrase,
            "name": phrase,
            "label": phrase,
            "score": int(score),
            "result_count": result_count,
            "occurrence_count": occurrence_count,
            "title_hits": int(stats["title_hits"]),
            "snippet_hits": int(stats["snippet_hits"]),
            "meta_hits": int(stats["meta_hits"]),
            "content_hits": int(stats["content_hits"]),
            "matched_queries": matched_queries,
            "evidence": stats["evidence"],
        })

    patterns.sort(
        key=lambda x: (
