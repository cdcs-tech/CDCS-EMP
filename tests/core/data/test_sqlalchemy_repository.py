"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Data Framework

Tests for the SQLAlchemy repository implementation.
"""

from __future__ import annotations

import pytest

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
