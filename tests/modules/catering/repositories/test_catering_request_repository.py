"""
Tests for the Catering Request repository.
"""

from unittest.mock import Mock

from app.modules.catering.models import CateringRequest
from app.modules.catering.repositories import CateringRequestRepository


def test_repository_uses_catering_request_model():
    """Verify the repository is bound to CateringRequest."""

    repository = CateringRequestRepository()

    assert isinstance(
        repository,
        CateringRequestRepository,
    )

    assert repository.model is CateringRequest


def test_repository_can_be_used_as_sqlalchemy_repository():
    """Verify the repository inherits the enterprise repository contract."""

    repository = CateringRequestRepository()

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

    repository = CateringRequestRepository()

    model = Mock(
        spec=CateringRequest
    )

    assert repository.model is CateringRequest
    assert model is not repository.model
