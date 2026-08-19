"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Data Framework

SQLAlchemy repository implementation.

Provides the database-backed implementation of the
generic BaseRepository contract without coupling
business services to SQLAlchemy directly.
"""

from __future__ import annotations

from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy import func, select

from app.core.data.entity import BaseEntity
from app.core.data.repository import BaseRepository
from app.extensions import db


TModel = TypeVar(
    "TModel",
    bound=BaseEntity,
)


class SQLAlchemyRepository(
    BaseRepository[TModel],
    Generic[TModel],
):
    """
    Generic SQLAlchemy repository.

    Provides database-backed persistence operations while
    preserving the BaseRepository abstraction.

    The repository deliberately does not commit or rollback
    transactions. Transaction ownership remains with the
    application's transaction boundary.
    """

    def __init__(
        self,
        model: Type[TModel],
    ) -> None:
        """
        Initialize the repository.

        Args:
            model:
                SQLAlchemy model class managed by this repository.

        Raises:
            ValueError:
                When no model class is supplied.
        """

        if model is None:
            raise ValueError(
                "A SQLAlchemy model class is required."
            )

        self.model = model

    def get_by_id(
        self,
        entity_id,
    ) -> Optional[TModel]:
        """
        Retrieve an entity by its primary key.

        Args:
            entity_id:
                Primary-key value.

        Returns:
            The matching entity or None.
        """

        return db.session.get(
            self.model,
            entity_id,
        )

    def get_all(
        self,
    ) -> List[TModel]:
        """
        Retrieve all entities.

        Returns:
            A list containing all persisted entities.
        """

        statement = select(
            self.model
        )

        return list(
            db.session.execute(
                statement
            ).scalars().all()
        )

    def add(
        self,
        entity: TModel,
    ) -> TModel:
        """
        Add and flush a new entity.

        The transaction is not committed here.

        Args:
            entity:
                SQLAlchemy model instance to persist.

        Returns:
            The persisted entity.
        """

        db.session.add(
            entity
        )

        db.session.flush()

        return entity

    def update(
        self,
        entity: TModel,
    ) -> TModel:
        """
        Update an existing entity.

        Detached instances are merged into the current
        SQLAlchemy session.

        The transaction is not committed here.

        Args:
            entity:
                Entity to update.

        Returns:
            The session-managed entity instance.
        """

        merged = db.session.merge(
            entity
        )

        db.session.flush()

        return merged

    def delete(
        self,
        entity: TModel,
    ) -> None:
        """
        Delete an entity.

        The transaction is not committed here.

        Args:
            entity:
                Entity to delete.
        """

        db.session.delete(
            entity
        )

        db.session.flush()

    def exists(
        self,
        entity_id,
    ) -> bool:
        """
        Determine whether an entity exists.

        Args:
            entity_id:
                Primary-key value.

        Returns:
            True when the entity exists, otherwise False.
        """

        statement = (
            select(
                func.count()
            )
            .select_from(
                self.model
            )
            .where(
                self.model.id == entity_id
            )
        )

        count = db.session.execute(
            statement
        ).scalar_one()

        return count > 0

    def count(
        self,
    ) -> int:
        """
        Return the total number of persisted entities.

        Returns:
            Number of persisted entities.
        """

        statement = select(
            func.count()
        ).select_from(
            self.model
        )

        return int(
            db.session.execute(
                statement
            ).scalar_one()
        )


__all__ = [
    "SQLAlchemyRepository",
]
