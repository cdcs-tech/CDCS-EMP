"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Data Framework

Base service abstraction.
"""

from __future__ import annotations

from typing import Generic, List, Optional, TypeVar

from app.core.data.entity import BaseEntity
from app.core.data.repository import BaseRepository

TEntity = TypeVar(
    "TEntity",
    bound=BaseEntity,
)


class BaseService(
    Generic[TEntity],
):
    """
    Base business service.

    Provides reusable CRUD operations while
    serving as the extension point for
    business rules and orchestration.
    """

    def __init__(
        self,
        repository: BaseRepository[TEntity],
    ):
        """
        Initialize the service.

        Args:
            repository:
                Repository used for data access.
        """
        self.repository = repository

    def get_by_id(
        self,
        entity_id,
    ) -> Optional[TEntity]:
        """
        Retrieve an entity by its identifier.
        """

        return self.repository.get_by_id(
            entity_id
        )

    def get_all(
        self,
    ) -> List[TEntity]:
        """
        Retrieve all entities.
        """

        return self.repository.get_all()

    def create(
        self,
        entity: TEntity,
    ) -> TEntity:
        """
        Create a new entity.

        Override in derived services to add
        business validation or workflows.
        """

        return self.repository.add(entity)

    def update(
        self,
        entity: TEntity,
    ) -> TEntity:
        """
        Update an existing entity.

        Override in derived services to add
        business validation or workflows.
        """

        return self.repository.update(entity)

    def delete(
        self,
        entity: TEntity,
    ) -> None:
        """
        Delete an entity.
        """

        self.repository.delete(entity)

    def exists(
        self,
        entity_id,
    ) -> bool:
        """
        Determine whether an entity exists.
        """

        return self.repository.exists(
            entity_id
        )

    def count(
        self,
    ) -> int:
        """
        Return the total number of entities.
        """

        return self.repository.count()
