from dataclasses import dataclass, asdict
from typing import Any, Dict, List


@dataclass
class ResearchItem:
    provider: str
    query: str
    title: str
    snippet: str
    url: str
    meta: Dict[str, Any]


@dataclass
class ResearchResult:
    provider: str
    query: str
    items: List[ResearchItem]

    def to_dict(self):
        return {
            "provider": self.provider,
            "query": self.query,
            "items": [asdict(x) for x in self.items],
        }
