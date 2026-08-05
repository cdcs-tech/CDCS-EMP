"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Data Framework

Reusable query models.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class QueryOptions:
    """
    Encapsulates query parameters used by
    repositories and services.
    """

    page: int = 1

    page_size: int = 25

    sort_by: str = "id"

    sort_direction: str = "asc"

    filters: Dict[str, Any] = field(
        default_factory=dict
    )

    search: str | None = None

    fields: List[str] = field(
        default_factory=list
    )

    include_inactive: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert query options to a dictionary.
        """

        return {
            "page": self.page,
            "page_size": self.page_size,
            "sort_by": self.sort_by,
            "sort_direction": self.sort_direction,
            "filters": dict(self.filters),
            "search": self.search,
            "fields": list(self.fields),
            "include_inactive": self.include_inactive,
        }
