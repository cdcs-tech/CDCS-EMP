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

from sqlalchemy import String, func, or_, select

from app.core.data.entity import BaseEntity
from app.core.data.pagination import PaginatedResult
from app.core.data.query import QueryOptions
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
        """

        return db.session.get(
            self.model,
            entity_id,
        )

    def get_all(
        self,
        options: QueryOptions | None = None,
    ) -> List[TModel]:
        """
        Retrieve all entities.

        When query options are supplied, the query is delegated
        to the provider-neutral query implementation so that
        filtering, searching, sorting, and pagination are
        applied consistently.

        Args:
            options:
                Optional Enterprise Data Framework query options.

        Returns:
            Entities matching the supplied query options.
        """

        if options is not None:
            return self.query(
                options
            )

        statement = select(
            self.model
        )

        return list(
            db.session.execute(
                statement
            ).scalars().all()
        )

    def query(
        self,
        options: QueryOptions,
    ) -> List[TModel]:
        """
        Execute a provider-neutral query.

        Supported query features:

        - filtering by mapped model attributes
        - case-insensitive partial text search
        - sorting by a mapped model attribute
        - ascending and descending sort direction
        - pagination

        The implementation deliberately does not interpret
        reporting-specific concepts.

        Args:
            options:
                Enterprise Data Framework query options.

        Returns:
            Entities matching the query options.

        Raises:
            ValueError:
                When invalid query options are supplied.
        """

        statement = self._build_query(
            options
        )

        statement = self._apply_pagination(
            statement,
            options,
        )

        return list(
            db.session.execute(
                statement
            ).scalars().all()
        )

    def paginate(
        self,
        options: QueryOptions,
    ) -> PaginatedResult[TModel]:
        """
        Execute a paginated query and return pagination metadata.

        Filtering and searching are applied before calculating
        the total record count so the metadata represents the
        same result set as the returned page.

        Args:
            options:
                Enterprise Data Framework query options.

        Returns:
            PaginatedResult containing matching entities and
            pagination metadata.

        Raises:
            ValueError:
                When invalid query options are supplied.
        """

        statement = self._build_query(
            options
        )

        count_statement = (
            select(
                func.count()
            )
            .select_from(
                statement
                .order_by(None)
                .subquery()
            )
        )

        total_records = int(
            db.session.execute(
                count_statement
            ).scalar_one()
        )

        paginated_statement = self._apply_pagination(
            statement,
            options,
        )

        items = list(
            db.session.execute(
                paginated_statement
            ).scalars().all()
        )

        return PaginatedResult(
            items=items,
            total_records=total_records,
            page=options.page,
            page_size=options.page_size,
        )

    def _build_query(
        self,
        options: QueryOptions,
    ):
        """
        Build the common filtered, searched, and sorted query.

        Pagination is deliberately excluded so that the same
        query can be used both for total-count calculation
        and page retrieval.
        """

        if not isinstance(
            options,
            QueryOptions,
        ):
            raise ValueError(
                "Query options must be a QueryOptions instance."
            )

        statement = select(
            self.model
        )

        statement = self._apply_filters(
            statement,
            options,
        )

        statement = self._apply_search(
            statement,
            options,
        )

        statement = self._apply_sorting(
            statement,
            options,
        )

        return statement

    def add(
        self,
        entity: TModel,
    ) -> TModel:
        """
        Add and flush a new entity.

        The transaction is not committed here.
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

    def _apply_filters(
        self,
        statement,
        options: QueryOptions,
    ):
        """
        Apply equality filters to a query.

        QueryOptions filters currently use the generic
        field/value representation. Operator-aware
        filtering remains the responsibility of the
        FilterCollection framework and a future query
        translation layer.
        """

        for field_name, value in options.filters.items():

            field = self._resolve_field(
                field_name
            )

            statement = statement.where(
                field == value
            )

        return statement

    def _apply_search(
        self,
        statement,
        options: QueryOptions,
    ):
        """
        Apply a generic case-insensitive text search.

        Search is performed as a partial match across all
        mapped SQLAlchemy string columns on the configured
        model.

        Non-string columns are deliberately excluded.

        Args:
            statement:
                SQLAlchemy select statement.

            options:
                Enterprise Data Framework query options.

        Returns:
            SQLAlchemy statement with search criteria applied.
        """

        if not options.search:
            return statement

        search_value = (
            f"%{options.search}%"
        )

        conditions = []

        for column in self.model.__table__.columns:

            if isinstance(
                column.type,
                String,
            ):
                conditions.append(
                    func.lower(
                        column
                    ).like(
                        search_value.lower()
                    )
                )

        if conditions:

            statement = statement.where(
                or_(
                    *conditions
                )
            )

        return statement

    def _apply_sorting(
        self,
        statement,
        options: QueryOptions,
    ):
        """
        Apply the requested sort order.
        """

        field = self._resolve_field(
            options.sort_by
        )

        if options.sort_direction == "desc":

            statement = statement.order_by(
                field.desc()
            )

        else:

            statement = statement.order_by(
                field.asc()
            )

        return statement

    def _apply_pagination(
        self,
        statement,
        options: QueryOptions,
    ):
        """
        Apply page and page-size settings.
        """

        offset = (
            options.page - 1
        ) * options.page_size

        return statement.offset(
            offset
        ).limit(
            options.page_size
        )

    def _resolve_field(
        self,
        field_name: str,
    ):
        """
        Resolve a query field against the configured model.

        Field resolution is deliberately restricted to
        mapped SQLAlchemy attributes.

        Raises:
            ValueError:
                When the requested field is unavailable.
        """

        if not isinstance(
            field_name,
            str,
        ):
            raise ValueError(
                "Query field name must be a string."
            )

        field_name = field_name.strip()

        if not field_name:
            raise ValueError(
                "Query field name is required."
            )

        field = getattr(
            self.model,
            field_name,
            None,
        )

        if field is None:

            raise ValueError(
                f"Unknown query field "
                f"'{field_name}'."
            )

        return field


__all__ = [
    "SQLAlchemyRepository",
]
