from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from core.file_utils import read_json, read_text


@dataclass
class BookPackage:
    book_id: str
    root: Path
    manifest: Dict[str, Any]
    story_bible_summary: Dict[str, Any] = field(default_factory=dict)
    characters: Dict[str, Any] = field(default_factory=dict)
    volume_summaries: Dict[str, Any] = field(default_factory=dict)
    chapter_metadata: Dict[str, Any] = field(default_factory=dict)
    hook_candidates: Dict[str, Any] = field(default_factory=dict)
    rights_info: Dict[str, Any] = field(default_factory=dict)
    sample_chapters: Dict[str, str] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

    @property
    def title(self) -> str:
        return self.manifest.get("title", self.book_id)

    @property
    def base_url(self) -> str:
        return self.manifest.get("base_url", f"https://example.com/book/{self.book_id}")

    @property
    def genre_text(self) -> str:
        genres = self.manifest.get("genre", [])
        if isinstance(genres, list):
            return ", ".join(genres)
        return str(genres)


REQUIRED = [
    "book_manifest.json",
    "sample_chapters/chapter_001.md",
    "sample_chapters/chapter_002.md",
    "sample_chapters/chapter_003.md",
]

RECOMMENDED = [
    "story_bible_summary.json",
    "characters.json",
    "volume_summaries.json",
    "chapter_metadata.json",
    "hook_candidates.json",
    "rights_info.json",
]


def load_book_package(input_root: Path, book_id: str) -> BookPackage:
    root = input_root / book_id
    warnings: List[str] = []

    if not root.exists():
        raise FileNotFoundError(f"Book input folder not found: {root}")

    missing_required = [rel for rel in REQUIRED if not (root / rel).exists()]
    if missing_required:
        raise FileNotFoundError("Missing required input files: " + ", ".join(missing_required))

    for rel in RECOMMENDED:
        if not (root / rel).exists():
            warnings.append(f"Recommended file missing: {rel}")

    manifest = read_json(root / "book_manifest.json", {})
    if not manifest.get("book_id"):
        manifest["book_id"] = book_id

    chapters = {}
    for i in range(1, 4):
        key = f"chapter_{i:03d}"
        chapters[key] = read_text(root / "sample_chapters" / f"{key}.md")

    rights = read_json(root / "rights_info.json", {})
    if rights and rights.get("rights_status") not in ("authorized_adaptation", "owned", "public_domain"):
        warnings.append("Rights status is not confirmed for paid campaigns.")
    if not rights:
        warnings.append("rights_info.json missing. Do not launch paid campaigns until rights are confirmed.")

    return BookPackage(
        book_id=book_id,
        root=root,
        manifest=manifest,
        story_bible_summary=read_json(root / "story_bible_summary.json", {}),
        characters=read_json(root / "characters.json", {}),
        volume_summaries=read_json(root / "volume_summaries.json", {}),
        chapter_metadata=read_json(root / "chapter_metadata.json", {}),
        hook_candidates=read_json(root / "hook_candidates.json", {}),
        rights_info=rights,
        sample_chapters=chapters,
        warnings=warnings,
    )
