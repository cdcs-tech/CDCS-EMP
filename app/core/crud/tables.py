"""
CDCS Enterprise Management Platform (CDCS-EMP)

Generic CRUD Framework

Enterprise table abstraction.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, List, TypeVar


from app.core.data import (
    BaseEntity,
)


TEntity = TypeVar(
    "TEntity",
    bound=BaseEntity,
)


@dataclass
class TableColumn:
    """
    Defines a table column.
    """

    name: str

    label: str

    sortable: bool = True

    visible: bool = True



class CRUDTable(
    Generic[TEntity],
):
    """
    Base enterprise table.

    Provides reusable table metadata
    and data formatting.
    """

    columns: List[TableColumn] = []


    def __init__(
        self,
        records: List[TEntity] | None = None,
    ):

        self.records = (
            records
            or []
        )


    def get_columns(
        self,
    ) -> List[TableColumn]:
        """
        Return table column definitions.
        """

        return list(
            self.columns
        )


    def get_rows(
        self,
    ) -> List[dict[str, Any]]:
        """
        Convert records into
        table rows.
        """

        rows = []

        for record in self.records:

            rows.append(
                record.__dict__
            )

        return rows


    def add_column(
        self,
        column: TableColumn,
    ) -> None:
        """
        Add dynamic column.
        """

        self.columns.append(
            column
        )
