"""
CDCS Enterprise Management Platform (CDCS-EMP)

Generic CRUD Framework

Reusable CRUD repository implementation.
"""

from __future__ import annotations

from typing import Generic, List, Optional, TypeVar

from app.core.data import (
    BaseEntity,
    BaseRepository,
)


TEntity = TypeVar(
    "TEntity",
    bound=BaseEntity,
)


class CRUDRepository(
    BaseRepository[TEntity],
    Generic[TEntity],
):
    """
    Generic CRUD repository.

    Provides the default repository
    implementation used by enterprise
    modules.
    """

    def __init__(self):
        self._storage: List[TEntity] = []

    def get_by_id(
        self,
        entity_id,
    ) -> Optional[TEntity]:
        """
        Retrieve entity by identifier.
        """

        for entity in self._storage:

            if entity.id == entity_id:
                return entity

        return None

    def get_all(
        self,
    ) -> List[TEntity]:
        """
        Retrieve all entities.
        """

        return list(
            self._storage
        )

    def add(
        self,
        entity: TEntity,
    ) -> TEntity:
        """
        Add new entity.
        """

        if entity.id is None:
            entity.id = (
                len(self._storage)
                + 1
            )

        self._storage.append(
            entity
        )

        return entity

    def update(
        self,
        entity: TEntity,
    ) -> TEntity:
        """
        Update existing entity.
        """

        for index, item in enumerate(
            self._storage
        ):

            if item.id == entity.id:

                self._storage[index] = entity

                return entity

        return self.add(entity)

    def delete(
        self,
        entity: TEntity,
    ) -> None:
        """
        Delete entity.
        """

        self._storage = [
            item
            for item in self._storage
            if item.id != entity.id
        ]

    def exists(
        self,
        entity_id,
    ) -> bool:
        """
        Check entity existence.
        """

        return (
            self.get_by_id(entity_id)
            is not None
        )

    def count(
        self,
    ) -> int:
        """
        Return entity count.
        """

        return len(
            self._storage
        )
