"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Data Framework

Tests for the SQLAlchemy repository implementation.
"""

from __future__ import annotations

import pytest

from app.core.data.pagination import PaginatedResult
from app.core.data.query import QueryOptions
from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)
from app.models.tenant import Tenant


class TestSQLAlchemyRepository:
    """
    Contract tests for SQLAlchemyRepository.
    """

    @pytest.fixture
    def repository(
        self,
        db_session,
    ):
        """
        Provide a repository bound to the Tenant model.

        The database-session dependency ensures that repository
        operations execute inside the Flask application context.
        """

        return SQLAlchemyRepository(
            Tenant
        )

    @pytest.fixture
    def tenant(self):
        """
        Provide a transient Tenant instance.
        """

        return Tenant(
            code="TEST-TENANT",
            name="Test Tenant",
            description="Repository test tenant",
        )

    def test_repository_requires_model(
        self,
    ):
        """
        A model class is required.
        """

        with pytest.raises(
            ValueError,
            match="SQLAlchemy model class is required",
        ):
            SQLAlchemyRepository(
                None
            )

    def test_repository_stores_model(
        self,
        repository,
    ):
        """
        Repository retains the configured model.
        """

        assert repository.model is Tenant

    def test_add_persists_entity_without_commit(
        self,
        repository,
        tenant,
        db_session,
    ):
        """
        Add flushes the entity but does not commit
        the transaction.
        """

        result = repository.add(
            tenant
        )

        assert result is tenant
        assert tenant.id is not None

        assert db_session.get(
            Tenant,
            tenant.id,
        ) is tenant

    def test_get_by_id_returns_entity(
        self,
        repository,
        tenant,
    ):
        """
        Retrieve an entity by primary key.
        """

        repository.add(
            tenant
        )

        result = repository.get_by_id(
            tenant.id
        )

        assert result is tenant

    def test_get_by_id_returns_none_for_missing_entity(
        self,
        repository,
    ):
        """
        Missing primary keys return None.
        """

        assert (
            repository.get_by_id(
                999999
            )
            is None
        )

    def test_get_all_returns_all_entities(
        self,
        repository,
    ):
        """
        Retrieve all persisted entities.
        """

        first = Tenant(
            code="TEST-001",
            name="Test Tenant 1",
        )

        second = Tenant(
            code="TEST-002",
            name="Test Tenant 2",
        )

        repository.add(
            first
        )

        repository.add(
            second
        )

        result = repository.get_all()

        assert first in result
        assert second in result
        assert len(result) == 2

    def test_update_merges_entity(
        self,
        repository,
        tenant,
    ):
        """
        Update an existing entity through merge.
        """

        repository.add(
            tenant
        )

        tenant_id = tenant.id

        tenant.name = "Updated Tenant"

        result = repository.update(
            tenant
        )

        assert result.id == tenant_id
        assert result.name == "Updated Tenant"

        refreshed = repository.get_by_id(
            tenant_id
        )

        assert refreshed.name == "Updated Tenant"

    def test_update_handles_detached_entity(
        self,
        repository,
        tenant,
        db_session,
    ):
        """
        Update supports an entity instance that is no
        longer attached to the active SQLAlchemy session.
        """

        repository.add(
            tenant
        )

        tenant_id = tenant.id

        db_session.expunge(
            tenant
        )

        tenant.name = "Detached Update"

        result = repository.update(
            tenant
        )

        assert result.id == tenant_id
        assert result.name == "Detached Update"

        refreshed = repository.get_by_id(
            tenant_id
        )

        assert refreshed.name == "Detached Update"

    def test_delete_removes_entity(
        self,
        repository,
        tenant,
    ):
        """
        Delete removes the entity from the session.
        """

        repository.add(
            tenant
        )

        tenant_id = tenant.id

        repository.delete(
            tenant
        )

        assert (
            repository.get_by_id(
                tenant_id
            )
            is None
        )

    def test_exists_returns_true_for_existing_entity(
        self,
        repository,
        tenant,
    ):
        """
        Existing entities are detected.
        """

        repository.add(
            tenant
        )

        assert repository.exists(
            tenant.id
        ) is True

    def test_exists_returns_false_for_missing_entity(
        self,
        repository,
    ):
        """
        Missing entities are not reported as existing.
        """

        assert repository.exists(
            999999
        ) is False

    def test_count_returns_entity_count(
        self,
        repository,
    ):
        """
        Count returns the number of persisted entities.
        """

        assert repository.count() == 0

        repository.add(
            Tenant(
                code="COUNT-001",
                name="Count Tenant 1",
            )
        )

        repository.add(
            Tenant(
                code="COUNT-002",
                name="Count Tenant 2",
            )
        )

        assert repository.count() == 2

    def test_repository_does_not_commit(
        self,
        repository,
        tenant,
        db_session,
    ):
        """
        Repository operations must not commit the transaction.

        Transaction ownership belongs to the transaction boundary.
        """

        repository.add(
            tenant
        )

        assert db_session.is_active is True

    # ------------------------------------------------------------------
    # QueryOptions integration
    # ------------------------------------------------------------------

    def test_get_all_accepts_query_options(
        self,
        repository,
    ):
        """
        Repository get_all supports the reusable QueryOptions contract.
        """

        first = Tenant(
            code="QUERY-001",
            name="Alpha Tenant",
        )

        second = Tenant(
            code="QUERY-002",
            name="Beta Tenant",
        )

        repository.add(
            first
        )

        repository.add(
            second
        )

        options = QueryOptions(
            page=1,
            page_size=25,
            sort_by="name",
            sort_direction="asc",
        )

        result = repository.get_all(
            options=options,
        )

        assert result == [
            first,
            second,
        ]

    def test_get_all_applies_pagination_options(
        self,
        repository,
    ):
        """
        Repository get_all applies QueryOptions pagination.
        """

        tenants = [
            Tenant(
                code=f"PAGE-{index:03d}",
                name=f"Tenant {index}",
            )
            for index in range(1, 6)
        ]

        for tenant in tenants:
            repository.add(
                tenant
            )

        options = QueryOptions(
            page=2,
            page_size=2,
            sort_by="id",
            sort_direction="asc",
        )

        result = repository.get_all(
            options=options,
        )

        assert len(result) == 2

        assert result[0].id == tenants[2].id
        assert result[1].id == tenants[3].id

    def test_get_all_applies_sorting_options(
        self,
        repository,
    ):
        """
        Repository get_all applies QueryOptions sorting.
        """

        first = Tenant(
            code="SORT-001",
            name="Charlie",
        )

        second = Tenant(
            code="SORT-002",
            name="Alpha",
        )

        third = Tenant(
            code="SORT-003",
            name="Bravo",
        )

        repository.add(
            first
        )

        repository.add(
            second
        )

        repository.add(
            third
        )

        options = QueryOptions(
            sort_by="name",
            sort_direction="asc",
        )

        result = repository.get_all(
            options=options,
        )

        assert [
            tenant.name
            for tenant in result
        ] == [
            "Alpha",
            "Bravo",
            "Charlie",
        ]

    def test_get_all_applies_descending_sorting(
        self,
        repository,
    ):
        """
        Repository get_all supports descending QueryOptions sorting.
        """

        first = Tenant(
            code="SORT-DESC-001",
            name="Alpha",
        )

        second = Tenant(
            code="SORT-DESC-002",
            name="Charlie",
        )

        third = Tenant(
            code="SORT-DESC-003",
            name="Bravo",
        )

        repository.add(
            first
        )

        repository.add(
            second
        )

        repository.add(
            third
        )

        options = QueryOptions(
            sort_by="name",
            sort_direction="desc",
        )

        result = repository.get_all(
            options=options,
        )

        assert [
            tenant.name
            for tenant in result
        ] == [
            "Charlie",
            "Bravo",
            "Alpha",
        ]

    def test_get_all_applies_filter_options(
        self,
        repository,
    ):
        """
        Repository get_all applies QueryOptions filters.
        """

        matching = Tenant(
            code="FILTER-001",
            name="Matching Tenant",
        )

        non_matching = Tenant(
            code="FILTER-002",
            name="Other Tenant",
        )

        repository.add(
            matching
        )

        repository.add(
            non_matching
        )

        options = QueryOptions(
            filters={
                "code": "FILTER-001",
            },
        )

        result = repository.get_all(
            options=options,
        )

        assert result == [
            matching,
        ]

    def test_get_all_applies_search_option(
        self,
        repository,
    ):
        """
        Repository get_all supports QueryOptions search criteria.
        """

        matching = Tenant(
            code="SEARCH-001",
            name="Finance Department",
            description="Finance operations",
        )

        non_matching = Tenant(
            code="SEARCH-002",
            name="Human Resources",
            description="HR operations",
        )

        repository.add(
            matching
        )

        repository.add(
            non_matching
        )

        options = QueryOptions(
            search="Finance",
        )

        result = repository.get_all(
            options=options,
        )

        assert result == [
            matching,
        ]

    def test_get_all_without_options_preserves_repository_contract(
        self,
        repository,
    ):
        """
        QueryOptions remains optional for backward compatibility.
        """

        first = Tenant(
            code="OPTIONAL-001",
            name="First Tenant",
        )

        second = Tenant(
            code="OPTIONAL-002",
            name="Second Tenant",
        )

        repository.add(
            first
        )

        repository.add(
            second
        )

        result = repository.get_all()

        assert first in result
        assert second in result
        assert len(result) == 2

    # ------------------------------------------------------------------
    # PaginatedResult integration
    # ------------------------------------------------------------------

    def test_paginate_returns_paginated_result(
        self,
        repository,
    ):
        """
        Repository paginate returns the reusable
        PaginatedResult contract.
        """

        tenants = [
            Tenant(
                code=f"PAGINATE-{index:03d}",
                name=f"Tenant {index}",
            )
            for index in range(1, 6)
        ]

        for tenant in tenants:
            repository.add(
                tenant
            )

        options = QueryOptions(
            page=2,
            page_size=2,
            sort_by="id",
            sort_direction="asc",
        )

        result = repository.paginate(
            options
        )

        assert isinstance(
            result,
            PaginatedResult,
        )

        assert result.items == [
            tenants[2],
            tenants[3],
        ]

        assert result.total_records == 5
        assert result.page == 2
        assert result.page_size == 2
        assert result.total_pages == 3
        assert result.has_previous is True
        assert result.has_next is True

    def test_paginate_counts_filtered_records(
        self,
        repository,
    ):
        """
        Pagination metadata reflects the filtered result set.
        """

        matching = [
            Tenant(
                code=f"FILTER-PAGE-{index:03d}",
                name=f"Matching {index}",
            )
            for index in range(1, 4)
        ]

        non_matching = Tenant(
            code="OTHER-PAGE-001",
            name="Other",
        )

        for tenant in matching:
            repository.add(
                tenant
            )

        repository.add(
            non_matching
        )

        options = QueryOptions(
            page=1,
            page_size=2,
            sort_by="id",
            sort_direction="asc",
            filters={
                "name": "Matching 1",
            },
        )

        result = repository.paginate(
            options
        )

        assert result.total_records == 1
        assert len(result.items) == 1
        assert result.items[0].name == "Matching 1"
        assert result.total_pages == 1
        assert result.has_previous is False
        assert result.has_next is False

    def test_paginate_counts_searched_records(
        self,
        repository,
    ):
        """
        Pagination metadata reflects the searched result set.
        """

        matching = Tenant(
            code="SEARCH-PAGE-001",
            name="Finance Department",
            description="Finance operations",
        )

        non_matching = Tenant(
            code="SEARCH-PAGE-002",
            name="Human Resources",
            description="HR operations",
        )

        repository.add(
            matching
        )

        repository.add(
            non_matching
        )

        options = QueryOptions(
            page=1,
            page_size=10,
            sort_by="id",
            search="Finance",
        )

        result = repository.paginate(
            options
        )

        assert result.total_records == 1
        assert result.items == [
            matching,
        ]

    def test_paginate_supports_empty_result_set(
        self,
        repository,
    ):
        """
        Pagination returns a valid empty result when
        no entities match.
        """

        options = QueryOptions(
            page=1,
            page_size=10,
            sort_by="id",
            filters={
                "code": "DOES-NOT-EXIST",
            },
        )

        result = repository.paginate(
            options
        )

        assert result.items == []
        assert result.total_records == 0
        assert result.total_pages == 0
        assert result.has_previous is False
        assert result.has_next is False
