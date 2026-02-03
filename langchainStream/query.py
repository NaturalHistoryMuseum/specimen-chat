from dataclasses import dataclass
from typing import Optional

@dataclass
class NHMQuery:
    scientific_name: Optional[str] = None
    country: Optional[str] = None
    year: Optional[str] = None
    limit: int = 20
    offset: int = 0
