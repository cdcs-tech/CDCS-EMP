"""
CDCS Enterprise Management Platform (CDCS-EMP)

Generic CRUD Framework

Reusable CRUD view foundation.
"""

from __future__ import annotations

from typing import Generic, TypeVar


from app.core.data import (
    BaseEntity,
)


from app.core.crud import (
    CRUDService,
)


TEntity = TypeVar(
    "TEntity",
    bound=BaseEntity,
)


class CRUDView(
    Generic[TEntity],
):
    """
    Base CRUD view abstraction.

    Provides common CRUD workflow
    coordination between UI and services.
    """

    def __init__(
        self,
        service: CRUDService[TEntity],
    ):
        self.service = service


    def list(
        self,
    ):
        """
        Return all entities.
        """

        return self.service.get_all()


    def detail(
        self,
        entity_id,
    ):
        """
        Return single entity.
        """

        return self.service.get(
            entity_id
        )


    def create(
        self,
        entity: TEntity,
    ):
        """
        Create entity.
        """

        return self.service.create(
            entity
        )


    def update(
        self,
        entity: TEntity,
    ):
        """
        Update entity.
        """

        return self.service.update(
            entity
        )


    def delete(
        self,
        entity_id,
    ):
        """
        Delete entity.
        """

        return self.service.delete(
            entity_id
        )
