"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Data Framework

Generic repository abstraction.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

from app.core.data.entity import BaseEntity
from app.core.data.query import QueryOptions


TEntity = TypeVar(
    "TEntity",
    bound=BaseEntity,
)


class BaseRepository(
    ABC,
    Generic[TEntity],
):
    """
    Generic repository contract for
    enterprise entities.
    """

    @abstractmethod
    def get_by_id(
        self,
        entity_id,
    ) -> Optional[TEntity]:
        """
        Retrieve an entity by its identifier.
        """

        raise NotImplementedError

    @abstractmethod
    def get_all(
        self,
    ) -> List[TEntity]:
        """
        Retrieve all entities.
        """

        raise NotImplementedError

    @abstractmethod
    def query(
        self,
        options: QueryOptions,
    ) -> List[TEntity]:
        """
        Execute a provider-neutral data query.

        Query interpretation remains the responsibility
        of the repository implementation.

        Args:
            options:
                Enterprise Data Framework query options.

        Returns:
            Entities matching the supplied query options.
        """

        raise NotImplementedError

    @abstractmethod
    def add(
        self,
        entity: TEntity,
    ) -> TEntity:
        """
        Persist a new entity.
        """

        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        entity: TEntity,
    ) -> TEntity:
        """
        Update an existing entity.
        """

        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        entity: TEntity,
    ) -> None:
        """
        Delete an entity.
        """

        raise NotImplementedError

    @abstractmethod
    def exists(
        self,
        entity_id,
    ) -> bool:
        """
        Determine whether an entity exists.
        """

        raise NotImplementedError

    @abstractmethod
    def count(
        self,
    ) -> int:
        """
        Return the total number of entities.
        """

        raise NotImplementedError
