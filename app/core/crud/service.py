"""
CDCS Enterprise Management Platform (CDCS-EMP)

Generic CRUD Framework

Reusable CRUD service implementation.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from app.core.data import (
    BaseEntity,
    BaseRepository,
    BaseService,
)

from app.core.crud.exceptions import (
    EntityNotFoundException,
)


TEntity = TypeVar(
    "TEntity",
    bound=BaseEntity,
)


class CRUDService(
    BaseService[TEntity],
    Generic[TEntity],
):
    """
    Generic CRUD service.

    Provides standard enterprise CRUD
    operations while allowing specialised
    services to extend behaviour.
    """

    def __init__(
        self,
        repository: BaseRepository[TEntity],
        entity_name: str | None = None,
    ):
        super().__init__(
            repository
        )

        self.entity_name = (
            entity_name
            or TEntity.__name__
        )

    def get(
        self,
        entity_id,
    ) -> TEntity:
        """
        Retrieve an entity.

        Raises:
            EntityNotFoundException
            when the entity does not exist.
        """

        entity = (
            self.repository.get_by_id(
                entity_id
            )
        )

        if entity is None:
            raise EntityNotFoundException(
                self.entity_name,
                entity_id,
            )

        return entity

    def create(
        self,
        entity: TEntity,
    ) -> TEntity:
        """
        Create an entity.
        """

        return (
            self.repository.add(
                entity
            )
        )

    def update(
        self,
        entity: TEntity,
    ) -> TEntity:
        """
        Update an entity.
        """

        return (
            self.repository.update(
                entity
            )
        )

    def delete(
        self,
        entity_id,
    ) -> None:
        """
        Delete an entity by identifier.
        """

        entity = self.get(
            entity_id
        )

        self.repository.delete(
            entity
        )
