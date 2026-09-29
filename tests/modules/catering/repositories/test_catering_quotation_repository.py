"""
Tests for the Catering Quotation repository.
"""

from unittest.mock import Mock

from app.modules.catering.models import CateringQuotation
from app.modules.catering.repositories import CateringQuotationRepository


def test_repository_uses_catering_quotation_model():
    """Verify the repository is bound to CateringQuotation."""

    repository = CateringQuotationRepository()

    assert isinstance(
        repository,
        CateringQuotationRepository,
    )

    assert repository.model is CateringQuotation


def test_repository_can_be_used_as_sqlalchemy_repository():
    """Verify the repository inherits the enterprise repository contract."""

    repository = CateringQuotationRepository()

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

    repository = CateringQuotationRepository()

    model = Mock(
        spec=CateringQuotation,
    )

    assert repository.model is CateringQuotation
    assert model is not repository.model
