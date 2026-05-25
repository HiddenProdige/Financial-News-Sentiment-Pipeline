# models.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Article:
    url: str
    headline: str
    body: str
    author: Optional[str]
    published_at: Optional[str]
    section: Optional[str]
    ticker: Optional[str] = None
    scraped_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
