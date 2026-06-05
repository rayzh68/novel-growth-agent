import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple


ROOT = Path(__file__).resolve().parent


READER_FIELDS = {
    "most_memorable_moment",
    "emotional_reaction",
    "why_i_would_or_would_not_keep_reading",
}


REVIEW_STRENGTH_FIELDS = {
    "commercial_strengths",
}


REVIEW_RISK_FIELDS = {
    "risk_flags",
    "main_problems",
}


GENERIC_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "being", "but", "by",
    "can", "could", "did", "do", "does", "doing", "for", "from", "had", "has",
    "have", "having", "he", "her", "hers", "him", "his", "i", "if", "in",
    "into", "is", "it", "its", "me", "my", "no", "not", "of", "on", "or",
    "our", "out", "over", "she", "so", "some", "such", "than", "that", "the",
    "their", "them", "then", "there", "these", "they", "this", "those", "to",
    "too", "up", "very", "was", "we", "were", "what", "when", "where", "which",
    "who", "whom", "whose", "why", "how", "will", "with", "would", "you",
    "your", "about", "after", "again", "also", "because", "before", "between",
    "both", "each", "even", "ever", "every", "get", "gets", "getting", "got",
    "just", "like", "make", "makes", "made", "may", "might", "more", "most",
    "much", "new", "now", "one", "only", "other", "same", "see", "seen",
    "still", "through", "use", "used", "using", "via", "while", "within",
    "without", "chapter", "chapters", "reader", "readers", "story", "stories",
    "book", "books", "novel", "novels", "fiction", "online", "web",

    "feel", "feels", "feeling", "felt", "need", "know", "knows", "knew",
    "exactly", "kind", "going", "seeing", "sense", "moment", "memorable",
    "reaction", "emotional"
}


SCHEMA_NOISE_TOKENS = {
    "score", "scores", "source", "sources", "file", "files", "path", "paths",
    "rewrite", "rewrites", "review", "reviews", "reviewer", "reviewers",
    "overall", "final", "draft", "drafts", "output", "input", "json", "txt",
    "md", "id", "ids", "version", "versions", "index", "count", "counts",
    "created", "created_at", "updated", "updated_at", "timestamp", "metadata",
    "meta", "field", "fields", "key", "keys", "value", "values",

    "project", "projects", "old", "name", "names", "hit", "hits",
    "diagnostic", "diagnostics", "metric", "metrics", "stat", "stats",
    "cjk", "chinese", "chars", "unicode", "replacement", "false", "true",
    "null", "none", "nan", "archive", "archived", "backup", "backups",
    "folder", "folders", "directory", "directories", "line", "lines",

    "memorable", "moment", "emotional", "reaction", "boring", "parts",
    "keep", "reading", "would", "commercial", "strength", "strengths",
    "risk", "flags", "main", "problems"

    "legacy",
    "variant",
    "variants",
    "raw",
    "extraction",
    "extract",
    "obsolete",
    "mojibake",
    "encoding",
    "encoded",
    "decode",
    "decoded",
    "garbled",
    "charset",
    "utf",
    "utf8",
    "utf-8",
    "latin",
    "ascii",
    "source-language",
    "language",
    "chinese-character",
    "character",
    "characters",
    "hostile",
    "allied",
    "neutral",
    "relation",
    "relations",
    "relationship",
    "relationships",
    "status",
    "state",
    "states",
    "detect",
    "detected",
    "detection",
    "normalize",
    "normalized",
    "normalization",
    "repair",
    "repaired",
    "fallback",
    "pipeline",
    "process",
    "processed",
    "processing",
    "alternate",
    "associated",
    "refer",
    "owned",
    "later",}


SCHEMA_NOISE_TOKENS = {
    "score", "scores", "source", "sources", "file", "files", "path", "paths",
    "rewrite", "rewrites", "review", "reviews", "reviewer", "reviewers",
    "overall", "final", "draft", "drafts", "output", "input", "json", "txt",
    "md", "id", "ids", "version", "versions", "index", "count", "counts",
    "created", "created_at", "updated", "updated_at", "timestamp", "metadata",
    "meta", "field", "fields", "key", "keys", "value", "values",

    "project", "projects", "old", "name", "names", "hit", "hits",
    "diagnostic", "diagnostics", "metric", "metrics", "stat", "stats",
    "cjk", "chinese", "chars", "unicode", "replacement", "false", "true",
    "null", "none", "nan", "archive", "archived", "backup", "backups",
    "folder", "folders", "directory", "directories", "line", "lines",

    "memorable", "moment", "emotional", "reaction", "boring", "parts",
    "keep", "reading", "would", "commercial", "strength", "strengths",
    "risk", "flags", "main", "problems"
}


BOUNDARY_STOPWORDS = GENERIC_STOPWORDS | {
    "after", "before", "during", "once", "until", "unless", "whereas",
    "whether", "while", "although", "though", "since"
}


WEAK_TOKENS = {
    "he", "she", "her", "him", "his", "hers", "they", "them", "their",
    "you", "your", "i", "me", "my", "we", "our", "it", "its", "this",
    "that", "these", "those", "when", "where", "why", "how", "what",
    "who", "whom", "whose"
}


TEXT_EXTENSIONS = {".txt", ".md", ".json"}


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
        return " ".join(compact_text(v) for v in value.values() if v is not None)
    return ""


def normalize_field_key(key: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(key).lower()).strip("_")


def expanded_field_names(field_names: Set[str]) -> Set[str]:
    result = set()

    for field in field_names:
        key = normalize_field_key(field)
        result.add(key)

        if key == "most_memorable_moment":
            result.add("memorable_moment")
        elif key == "emotional_reaction":
            result.add("emotional_response")
            result.add("reader_reaction")
        elif key == "why_i_would_or_would_not_keep_reading":
            result.add("why_keep_reading")
            result.add("keep_reading_reason")
            result.add("reading_reason")
            result.add("would_keep_reading")
        elif key == "commercial_strengths":
            result.add("commercial_strength")
            result.add("strengths")
        elif key == "risk_flags":
            result.add("risks")
            result.add("flags")
        elif key == "main_problems":
            result.add("problems")
            result.add("issues")

    return result


def looks_like_path_or_machine_text(text: str) -> bool:
    lowered = text.lower()

    if "\\" in text or "/" in text:
        if any(ext in lowered for ext in [".json", ".txt", ".md", ".py"]):
            return True

    if "novel-mvp" in lowered or "novel_growth" in lowered or "novel-growth" in lowered:
        return True

    if re.search(r"\b[a-z]:\\", lowered):
        return True

    if re.search(r"\b\w+_\w+_\w+\b", lowered) and len(text.split()) < 12:
        return True

    return False


def is_natural_feedback_text(text: str) -> bool:
    text = compact_text(text)
    if not text:
        return False

    if looks_like_path_or_machine_text(text):
        return False

    tokens = tokenize(text)
    if len(tokens) < 5:
        return False

    clean = [
        t for t in tokens
        if t not in GENERIC_STOPWORDS and t not in SCHEMA_NOISE_TOKENS
    ]

    if len(clean) < 3:
        return False

    noise_count = sum(1 for t in tokens if t in SCHEMA_NOISE_TOKENS)
    if noise_count / max(len(tokens), 1) >= 0.35:
        return False

    return True


def natural_texts_from_value(value: Any) -> List[str]:
    result: List[str] = []

    if value is None:
        return result

    if isinstance(value, str):
        text = compact_text(value)
        if is_natural_feedback_text(text):
            result.append(text)
        return result

    if isinstance(value, (int, float, bool)):
        return result

    if isinstance(value, list):
        for item in value:
            result.extend(natural_texts_from_value(item))
        return result

    if isinstance(value, dict):
        for key, val in value.items():
            key_text = normalize_field_key(str(key))

            if key_text in SCHEMA_NOISE_TOKENS:
                continue

            result.extend(natural_texts_from_value(val))

        return result

    return result


def collect_json_fields(value: Any, field_names: Set[str]) -> List[str]:
    found: List[str] = []
    target_fields = expanded_field_names(field_names)

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, val in node.items():
                key_text = normalize_field_key(str(key))

                if key_text in target_fields:
                    found.extend(natural_texts_from_value(val))

                walk(val)

        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(value)

    deduped = []
    seen = set()

    for item in found:
        marker = item.lower()
        if marker in seen:
            continue
        seen.add(marker)
        deduped.append(item)

    return deduped


def extract_plaintext_field_sections(raw: str, field_names: Set[str]) -> List[str]:
    target_fields = expanded_field_names(field_names)
    paragraphs = re.split(r"\n\s*\n+", raw)
    found: List[str] = []

    for para in paragraphs:
        normalized_para = normalize_field_key(para[:180])

        if not any(field in normalized_para for field in target_fields):
            continue

        cleaned = para
        cleaned = re.sub(r"(?i)most[_\s-]*memorable[_\s-]*moment\s*[:：-]*", " ", cleaned)
        cleaned = re.sub(r"(?i)memorable[_\s-]*moment\s*[:：-]*", " ", cleaned)
        cleaned = re.sub(r"(?i)emotional[_\s-]*(reaction|response)\s*[:：-]*", " ", cleaned)
        cleaned = re.sub(r"(?i)why[_\s-]*i[_\s-]*would[_\s-]*or[_\s-]*would[_\s-]*not[_\s-]*keep[_\s-]*reading\s*[:：-]*", " ", cleaned)
        cleaned = re.sub(r"(?i)why[_\s-]*keep[_\s-]*reading\s*[:：-]*", " ", cleaned)
        cleaned = re.sub(r"(?i)commercial[_\s-]*strengths?\s*[:：-]*", " ", cleaned)
        cleaned = re.sub(r"(?i)risk[_\s-]*flags?\s*[:：-]*", " ", cleaned)
        cleaned = re.sub(r"(?i)main[_\s-]*problems?\s*[:：-]*", " ", cleaned)

        cleaned = compact_text(cleaned)

        if is_natural_feedback_text(cleaned):
            found.append(cleaned)

    return found


def load_texts_from_dir(path: Path, field_names: Set[str] | None = None) -> List[str]:
    texts: List[str] = []

    if not path.exists():
        return texts

    for file_path in sorted(path.rglob("*")):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in TEXT_EXTENSIONS:
            continue

        try:
            raw = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        if not raw.strip():
            continue

        if file_path.suffix.lower() == ".json":
            try:
                data = json.loads(raw)
                if field_names:
                    selected = collect_json_fields(data, field_names)
                    if selected:
                        texts.extend(selected)
                else:
                    texts.append(compact_text(data))
            except Exception:
                texts.append(raw)
