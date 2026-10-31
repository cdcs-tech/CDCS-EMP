"""
Tests for the Catering Revenue repository.
"""

from unittest.mock import Mock, patch

from sqlalchemy.dialects import mssql

from app.modules.catering.models import CateringRevenue
from app.modules.catering.repositories import CateringRevenueRepository


def test_repository_uses_catering_revenue_model():
    """Verify the repository is bound to CateringRevenue."""

    repository = CateringRevenueRepository()

    assert isinstance(
        repository,
        CateringRevenueRepository,
    )

    assert repository.model is CateringRevenue


def test_repository_can_be_used_as_sqlalchemy_repository():
    """Verify the repository inherits the enterprise repository contract."""

    repository = CateringRevenueRepository()

    assert hasattr(
        repository,
        "get_by_id",
    )

    assert hasattr(
        repository,
        "get_all",
    )

    assert hasattr(
        repository,
        "add",
    )

    assert hasattr(
        repository,
        "update",
    )

    assert hasattr(
        repository,
        "delete",
    )


def test_repository_model_reference_is_stable():
    """Verify the repository retains the expected model reference."""

    repository = CateringRevenueRepository()

    model = Mock(
        spec=CateringRevenue
    )

    assert repository.model is CateringRevenue
    assert model is not repository.model


def test_get_recognized_by_event_id_queries_recognized_revenue():
    """Verify recognized revenue is retrieved by Catering Event."""

    repository = CateringRevenueRepository()

    recognized_revenue = Mock(
        spec=CateringRevenue
    )

    session = Mock()
    session.execute.return_value.scalar_one_or_none.return_value = (
        recognized_revenue
    )

    with patch(
        "app.modules.catering.repositories.catering_revenue.db.session",
        session,
    ):
        result = repository.get_recognized_by_event_id(42)

    assert result is recognized_revenue

    session.execute.assert_called_once()

    statement = session.execute.call_args.args[0]
    compiled = str(
        statement.compile(
            dialect=mssql.dialect(),
            compile_kwargs={"literal_binds": True}
        )
    )

    assert "catering_revenues.event_id" in compiled
    assert "42" in compiled
    assert "catering_revenues.status" in compiled
    assert "RECOGNIZED" in compiled
    assert "catering_revenues.is_deleted" in compiled
    assert "catering_revenues.is_deleted = 0" in compiled
    assert "catering_revenues.is_deleted IS 0" not in compiled
