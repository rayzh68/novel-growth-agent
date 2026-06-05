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
        else:
            if field_names:
                texts.extend(extract_plaintext_field_sections(raw, field_names))
            else:
                texts.append(raw)

    return [t for t in texts if t.strip()]


def normalize_token(token: str) -> str:
    token = str(token).lower().replace("’", "'").strip("-'")
    token = re.sub(r"'s$", "", token)
    token = token.replace("'", "")
    token = token.strip("-'")
    return token


def tokenize(text: str) -> List[str]:
    raw = re.findall(r"[a-z][a-z'\-]{1,}|[\u4e00-\u9fff]{2,}", text.lower())
    tokens: List[str] = []

    for token in raw:
        token = normalize_token(token)
        if not token:
            continue
        if len(token) < 2:
            continue
        tokens.append(token)

    return tokens


def content_tokens(text: str) -> List[str]:
    return [
        t for t in tokenize(text)
        if t not in GENERIC_STOPWORDS and t not in SCHEMA_NOISE_TOKENS
    ]


def normalize_phrase(text: str) -> str:
    return " ".join(tokenize(text))


def entity_token_set(entity_phrases: Set[str] | None = None) -> Set[str]:
    tokens: Set[str] = set()

    for phrase in entity_phrases or set():
        for token in tokenize(phrase):
            if token and token not in GENERIC_STOPWORDS:
                tokens.add(token)

    return tokens


def proper_name_phrases(text: str) -> Set[str]:
    names: Set[str] = set()

    for match in re.finditer(r"\b[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,}){0,2}\b", text):
        phrase = match.group(0).strip()
        lowered = normalize_phrase(phrase)
        parts = lowered.split()

        if len(parts) >= 2:
            names.add(lowered)

    return names


def token_has_schema_noise(token: str) -> bool:
    token = normalize_token(token)

    if not token:
        return True

    if token in SCHEMA_NOISE_TOKENS:
        return True

    parts = [p for p in re.split(r"[-_/]+", token) if p]
    if any(p in SCHEMA_NOISE_TOKENS for p in parts):
        return True

    return False


def contains_schema_noise_phrase(phrase: str) -> bool:
    words = tokenize(phrase)

    if not words:
        return True

    if any(token_has_schema_noise(w) for w in words):
        return True

    return False


def weak_phrase(phrase: str, entity_phrases: Set[str] | None = None) -> bool:
    entity_phrases = entity_phrases or set()

    phrase = normalize_phrase(phrase)
    if not phrase:
        return True

    if "http" in phrase or "www" in phrase:
        return True

    if contains_schema_noise_phrase(phrase):
        return True

    words = phrase.split()

    if len(words) < 2 or len(words) > 4:
        return True

    if phrase in entity_phrases:
        return True

    if words[0] in BOUNDARY_STOPWORDS or words[-1] in BOUNDARY_STOPWORDS:
        return True

    if any(w in WEAK_TOKENS for w in words):
        return True

    strong_words = [
        w for w in words
        if w not in GENERIC_STOPWORDS
        and w not in SCHEMA_NOISE_TOKENS
        and not token_has_schema_noise(w)
    ]

    if len(strong_words) < 2:
        return True

    if len(set(strong_words)) == 1:
        return True

    if any(w in SCHEMA_NOISE_TOKENS for w in words):
        return True

    if all(w in SCHEMA_NOISE_TOKENS for w in strong_words):
        return True

    entity_tokens = entity_token_set(entity_phrases)

    if entity_tokens:
        entity_count = sum(1 for w in strong_words if w in entity_tokens)

        if entity_count == len(strong_words):
            return True

        if len(strong_words) <= 2 and entity_count >= 1:
            return True

        if len(strong_words) <= 4 and entity_count >= 2:
            return True

    return False

def extract_phrases(
    texts: Iterable[str],
    limit: int = 30,
    entity_phrases: Set[str] | None = None,
    min_n: int = 2,
    max_n: int = 4,
) -> List[Dict[str, Any]]:
    entity_phrases = entity_phrases or set()
    entity_tokens = entity_token_set(entity_phrases)
    counts: Counter = Counter()

    for text in texts:
        text = compact_text(text)
        if not text:
            continue

        tokens = tokenize(text)

        filtered = [
            t for t in tokens
            if t not in GENERIC_STOPWORDS
            and t not in SCHEMA_NOISE_TOKENS
            and t not in entity_tokens
            and not token_has_schema_noise(t)
        ]

        for n in range(min_n, max_n + 1):
            if len(filtered) < n:
                continue

            for i in range(0, len(filtered) - n + 1):
                phrase = " ".join(filtered[i:i + n])

                if weak_phrase(phrase, entity_phrases):
                    continue

                counts[phrase] += 1

    result = []

    for phrase, count in counts.most_common(limit * 6):
        if weak_phrase(phrase, entity_phrases):
            continue

        result.append({
            "signal": phrase,
            "phrase": phrase,
            "count": int(count),
        })

        if len(result) >= limit:
            break

    return result

def phrase_text(item: Any) -> str:
    if isinstance(item, str):
        return item

    if isinstance(item, dict):
        for key in ["signal", "pattern", "phrase", "name", "label", "theme", "driver"]:
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    return compact_text(item)


def unique_by_phrase(items: List[Dict[str, Any]], key: str = "signal", limit: int = 30) -> List[Dict[str, Any]]:
    seen = set()
    result = []

    for item in items:
        phrase = normalize_phrase(str(item.get(key, "")))
        if not phrase or phrase in seen:
            continue
        seen.add(phrase)
        result.append(item)
        if len(result) >= limit:
            break

    return result



STORY_SEED_NOISE_TOKENS = {
    # engineering / encoding / migration contamination
    "legacy", "variant", "variants", "raw", "extraction", "extract",
    "obsolete", "mojibake", "encoding", "encoded", "decode", "decoded",
    "garbled", "charset", "utf", "utf8", "latin", "ascii",
    "source-language", "chinese-character",

    # relationship table enums / schema values
    "hostile", "allied", "neutral", "alternate", "associated",
    "owned", "later", "refer",

    # pipeline / processing contamination
    "detect", "detected", "detection", "normalize", "normalized",
    "normalization", "repair", "repaired", "fallback", "pipeline",
    "process", "processed", "processing",
}


STORY_SEED_NOISE_PHRASES = {
    "source language",
    "chinese character",
    "chinese characters",
    "raw extraction",
    "legacy chinese character",
    "legacy chinese characters",
    "mojibake variants",
    "variants raw",
    "extraction obsolete",
    "hostile allied",
    "allied neutral",
    "hostile allied neutral",
    "associated alternate",
    "alternate legacy",
    "owned legacy",
    "later legacy",
}


def story_seed_has_noise(text: str) -> bool:
    normalized = normalize_phrase(text)
    if not normalized:
        return True

    normalized_space = normalized.replace("-", " ")
    words = set(normalized.split()) | set(normalized_space.split())

    if words & STORY_SEED_NOISE_TOKENS:
        return True

    for phrase in STORY_SEED_NOISE_PHRASES:
        if phrase in normalized_space:
            return True

    return False


def collect_story_entity_names_from_value(value: Any) -> Set[str]:
    names: Set[str] = set()

    def add_candidate(candidate: Any) -> None:
        text_value = compact_text(candidate)
        tokens = tokenize(text_value)

        if 1 <= len(tokens) <= 4:
            phrase = " ".join(tokens)
            if not story_seed_has_noise(phrase):
                names.add(phrase)

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, val in node.items():
                key_text = re.sub(r"[^a-z0-9]+", "_", str(key).lower()).strip("_")

                if key_text in {
                    "name",
                    "full_name",
                    "english_name",
                    "display_name",
                    "character_name",
                    "alias",
                    "aliases",
                }:
                    if isinstance(val, list):
                        for item in val:
                            add_candidate(item)
                    else:
                        add_candidate(val)

                walk(val)

        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(value)
    return names


def collect_story_entity_names_from_dir(path: Path, raw_texts: List[str]) -> Set[str]:
    names: Set[str] = set()

    for raw in raw_texts:
        for item in proper_name_phrases(raw):
            if not story_seed_has_noise(item):
                names.add(item)

    if not path.exists():
        return names

    for file_path in sorted(path.rglob("*")):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() != ".json":
            continue

        try:
            data = json.loads(file_path.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            continue

        names.update(collect_story_entity_names_from_value(data))

    return names


def split_story_candidate_segments(text: str) -> List[str]:
    text = compact_text(text)

    if not text:
        return []

    parts = re.split(r"[\r\n]+|(?<=[.!?。！？])\s+|[;；]", text)
    result: List[str] = []

    for part in parts:
        part = compact_text(part)
        if not part:
            continue

        tokens = tokenize(part)

        if len(tokens) < 4:
            continue

        if len(tokens) > 80:
            continue

        if story_seed_has_noise(part):
            continue

        result.append(part)

    return result


def filter_story_boundary_texts(texts: List[str]) -> List[str]:
    segments: List[str] = []

    for text in texts:
        segments.extend(split_story_candidate_segments(text))

    return segments


def summarize_story_bible(book: str) -> Tuple[List[Dict[str, Any]], Set[str]]:
    path = ROOT / "input" / book / "story_bible-001"
    texts = load_texts_from_dir(path)

    raw_texts: List[str] = []

    if path.exists():
        for file_path in sorted(path.rglob("*")):
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() not in TEXT_EXTENSIONS:
                continue

            try:
                raw_texts.append(file_path.read_text(encoding="utf-8", errors="ignore"))
            except Exception:
                continue

    full_text = "\n".join(raw_texts + texts)

    names = collect_story_entity_names_from_dir(path, raw_texts + texts)
    names.update(item for item in proper_name_phrases(full_text) if not story_seed_has_noise(item))

    clean_texts = filter_story_boundary_texts(texts)

    seeds = extract_phrases(clean_texts, limit=30, entity_phrases=names)

    cleaned_seeds: List[Dict[str, Any]] = []
    seen = set()

    for seed in seeds:
        phrase = normalize_phrase(str(seed.get("signal") or seed.get("phrase") or ""))
        if not phrase:
            continue
        if story_seed_has_noise(phrase):
            continue
        if phrase in seen:
            continue

        seen.add(phrase)
        cleaned_seeds.append(seed)

        if len(cleaned_seeds) >= 30:
            break

    return cleaned_seeds, names


def summarize_readers(book: str, entity_phrases: Set[str]) -> List[Dict[str, Any]]:
    path = ROOT / "input" / book / "reader-001"
    texts = load_texts_from_dir(path, READER_FIELDS)
    return extract_phrases(texts, limit=30, entity_phrases=entity_phrases)


def summarize_reviews(book: str, entity_phrases: Set[str]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    path = ROOT / "input" / book / "reviewer-001"
    review_texts = load_texts_from_dir(path, REVIEW_STRENGTH_FIELDS)
    risk_texts = load_texts_from_dir(path, REVIEW_RISK_FIELDS)

    review_signals = extract_phrases(review_texts, limit=30, entity_phrases=entity_phrases)
    risk_signals = extract_phrases(risk_texts, limit=30, entity_phrases=entity_phrases)

    return review_signals, risk_signals


def load_market_patterns(book: str) -> List[Dict[str, Any]]:
    path = ROOT / "output" / "market_research" / f"{book}_market_research.json"
    data = read_json(path) or {}

    patterns = data.get("market_patterns", [])
    result = []

    for item in patterns:
        phrase = phrase_text(item)
        phrase = normalize_phrase(phrase)

        if not phrase:
            continue

        copied = dict(item) if isinstance(item, dict) else {}
        copied["pattern"] = phrase
        copied["score"] = int(copied.get("score", 0) or 0)
        result.append(copied)

    return result


def token_set(text: str) -> Set[str]:
    return set(content_tokens(text))


def overlap_size(a: str, b: str) -> int:
    left = token_set(a)
    right = token_set(b)

    if not left or not right:
        return 0

    return len(left & right)


def top_overlaps(
    source: str,
    items: List[Dict[str, Any]],
    label_key: str,
    limit: int = 6,
    min_overlap: int = 1,
) -> List[Dict[str, Any]]:
    rows = []

    for item in items:
        text = phrase_text(item)
        common = overlap_size(source, text)

        if common < min_overlap:
            continue

        rows.append({
            label_key: text,
            "overlap": int(common),
            "score": int(item.get("score", item.get("count", 0)) or 0),
        })

    rows.sort(key=lambda x: (x["overlap"], x["score"]), reverse=True)
    return rows[:limit]



QUERY_SEED_NOISE_TOKENS = {
    # document / report / instruction noise, not genre taxonomy
    "batch", "batches", "report", "reports", "provided", "insufficient",
    "manual", "block", "primary", "fully", "stated", "explicitly",
    "should", "against", "refer", "owned", "later", "associated",
    "alternate", "legacy", "mojibake", "raw", "extraction", "obsolete",
}


def query_safe_story_seed(term: str, entity_phrases: Set[str] | None = None) -> bool:
    term = normalize_phrase(term)
    if not term:
        return False

    if "story_seed_has_noise" in globals() and story_seed_has_noise(term):
        return False

    if weak_phrase(term, entity_phrases or set()):
        return False

    tokens = content_tokens(term)
    if len(tokens) < 2:
        return False

    if any(t in QUERY_SEED_NOISE_TOKENS for t in tokens):
        return False

    entity_tokens = entity_token_set(entity_phrases or set())
    if entity_tokens:
        entity_count = sum(1 for t in tokens if t in entity_tokens)

        # 任何含角色/人名 token 的 seed，都不进外部市场 query。
        if entity_count > 0:
            return False

    return True


def build_research_query_plan(
    reader_signals: List[Dict[str, Any]],
    story_seeds: List[Dict[str, Any]],
    entity_phrases: Set[str] | None = None,
) -> Tuple[List[str], List[Dict[str, Any]]]:
    queries = []
    plan = []

    entity_phrases = entity_phrases or set()

    reader_terms = []
    seen_reader_terms = set()

    for item in reader_signals[:30]:
        term = normalize_phrase(phrase_text(item))
        if not term:
            continue

        if weak_phrase(term, entity_phrases):
            continue

        if term in seen_reader_terms:
            continue

        seen_reader_terms.add(term)
        reader_terms.append(term)

    for reader_term in reader_terms:
        base_queries = [
            f"{reader_term} reader discussion",
            f"{reader_term} web novel audience",
            f"{reader_term} online fiction audience",
        ]

        for query in base_queries:
            if query not in queries:
                queries.append(query)
                plan.append({
                    "source": "reader_signal",
                    "signal": reader_term,
                    "query": query,
                })

        if len(queries) >= 40:
            break

    return queries[:40], plan[:40]

def build_core_themes(
    story_seeds: List[Dict[str, Any]],
    reader_signals: List[Dict[str, Any]],
    market_patterns: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    rows = []

    for seed in story_seeds:
        seed_text = phrase_text(seed)

        reader_hits = top_overlaps(seed_text, reader_signals, "reader_signal", limit=4)
        market_hits = top_overlaps(seed_text, market_patterns, "market_pattern", limit=4)

        if not reader_hits and not market_hits:
            continue

        score = int(seed.get("count", 0) or 0) + len(reader_hits) * 3 + len(market_hits) * 5

        rows.append({
            "theme": seed_text,
            "score": score,
            "reader_evidence": reader_hits,
            "market_evidence": market_hits,
        })

    rows.sort(key=lambda x: x["score"], reverse=True)
    return rows[:20]


def build_market_drivers(
    reader_signals: List[Dict[str, Any]],
    market_patterns: List[Dict[str, Any]],
    story_seeds: List[Dict[str, Any]],
    review_signals: List[Dict[str, Any]],
    risk_signals: List[Dict[str, Any]],
    entity_phrases: Set[str],
) -> List[Dict[str, Any]]:
    rows = []

    for signal in reader_signals:
        driver = phrase_text(signal)
        driver = normalize_phrase(driver)

        if weak_phrase(driver, entity_phrases):
            continue

        market_hits = top_overlaps(
            driver,
            market_patterns,
            "market_pattern",
            limit=8,
            min_overlap=2,
        )

        if not market_hits:
            continue

        story_hits = top_overlaps(driver, story_seeds, "story_seed", limit=5)
        review_hits = top_overlaps(driver, review_signals, "review_signal", limit=5)
        risk_hits = top_overlaps(driver, risk_signals, "risk_signal", limit=5)

        score = (
            int(signal.get("count", 0) or 0) * 2
            + sum(int(x.get("score", 0) or 0) for x in market_hits)
            + len(market_hits) * 10
            + len(story_hits) * 3
            + len(review_hits) * 4
            - len(risk_hits) * 2
        )

        rows.append({
            "driver": driver,
            "source": "reader_signal",
            "score": int(score),
            "source_signal": signal,
            "matched_market_patterns": market_hits,
            "story_evidence": story_hits,
            "review_evidence": review_hits,
            "risk_evidence": risk_hits,
        })

    rows.sort(key=lambda x: x["score"], reverse=True)

    deduped = []
    seen = set()

    for row in rows:
        key = normalize_phrase(row["driver"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)

        if len(deduped) >= 20:
            break

    return deduped


def build_profile(book: str) -> Dict[str, Any]:
    story_seeds, entity_phrases = summarize_story_bible(book)
    reader_signals = summarize_readers(book, entity_phrases)
    review_signals, risk_signals = summarize_reviews(book, entity_phrases)
    market_patterns = load_market_patterns(book)

    research_queries, research_query_plan = build_research_query_plan(reader_signals, story_seeds, entity_phrases)

    core_themes = build_core_themes(
        story_seeds=story_seeds,
        reader_signals=reader_signals,
        market_patterns=market_patterns,
    )

    market_drivers = build_market_drivers(
        reader_signals=reader_signals,
        market_patterns=market_patterns,
        story_seeds=story_seeds,
        review_signals=review_signals,
        risk_signals=risk_signals,
        entity_phrases=entity_phrases,
    )

    return {
        "book_id": book,
        "created_at": utc_now(),
        "source_dirs": {
            "story_bible": f"input/{book}/story_bible-001",
            "reader": f"input/{book}/reader-001",
            "reviewer": f"input/{book}/reviewer-001",
            "market_research": f"output/market_research/{book}_market_research.json",
        },
        "story_seeds": story_seeds,
        "reader_signals": reader_signals,
        "review_signals": review_signals,
        "risk_signals": risk_signals,
        "research_queries": research_queries,
        "research_query_plan": research_query_plan,
        "core_themes": core_themes,
        "market_drivers": market_drivers,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", required=True)
    args = parser.parse_args()

    profile = build_profile(args.book)

    out_path = ROOT / "output" / "market_profiles" / f"{args.book}_market_profile.json"
    write_json(out_path, profile)

    print(f"OK: saved {out_path.relative_to(ROOT)}")
    print(json.dumps({
        "book_id": profile["book_id"],
        "story_seeds": len(profile["story_seeds"]),
        "reader_signals": len(profile["reader_signals"]),
        "review_signals": len(profile["review_signals"]),
        "risk_signals": len(profile["risk_signals"]),
        "research_queries": len(profile["research_queries"]),
        "core_themes": len(profile["core_themes"]),
        "market_drivers": len(profile["market_drivers"]),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
