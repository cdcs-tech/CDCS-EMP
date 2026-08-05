"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Data Framework

Public interface for reusable enterprise
data abstractions.
"""

from app.core.data.entity import (
    BaseEntity,
)

from app.core.data.repository import (
    BaseRepository,
)

from app.core.data.service import (
    BaseService,
)

from app.core.data.query import (
    QueryOptions,
)

from app.core.data.filters import (
    Filter,
    FilterCollection,
)

from app.core.data.pagination import (
    Pagination,
    PaginatedResult,
)

from app.core.data.sorting import (
    SortDirection,
    SortDefinition,
    SortCollection,
)

__all__ = [

    "BaseEntity",

    "BaseRepository",

    "BaseService",

    "QueryOptions",

    "Filter",

    "FilterCollection",

    "Pagination",

    "PaginatedResult",

    "SortDirection",

    "SortDefinition",

    "SortCollection",

]
