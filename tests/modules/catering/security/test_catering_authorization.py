from unittest.mock import Mock

import pytest

from app.core.security.exceptions import PermissionDeniedError
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)


def test_authorization_adapter_requires_callable_evaluator():
    with pytest.raises(ValueError, match="Authorization evaluator is required"):
        CateringAuthorizationAdapter(evaluator=None)


def test_authorization_adapter_rejects_non_callable_evaluator():
    with pytest.raises(ValueError, match="Authorization evaluator is required"):
        CateringAuthorizationAdapter(evaluator="not-callable")


def test_authorization_adapter_requires_permission_code():
    adapter = CateringAuthorizationAdapter(
        evaluator=lambda subject, permission: True,
    )

    with pytest.raises(ValueError, match="Permission code is required"):
        adapter.authorize(
            subject="test-user",
            permission_code="",
        )


def test_authorization_adapter_allows_authorized_operation():
    evaluator = Mock(return_value=True)

    adapter = CateringAuthorizationAdapter(
        evaluator=evaluator,
    )

    result = adapter.authorize(
        subject="test-user",
        permission_code="CATERING.STOCK_MOVEMENT.POST",
    )

    assert result is True
    evaluator.assert_called_once_with(
        "test-user",
        "CATERING.STOCK_MOVEMENT.POST",
    )


def test_authorization_adapter_denies_unauthorized_operation():
    adapter = CateringAuthorizationAdapter(
        evaluator=lambda subject, permission: False,
    )

    with pytest.raises(
        PermissionDeniedError,
        match="CATERING.STOCK_MOVEMENT.POST",
    ):
        adapter.authorize(
            subject="test-user",
            permission_code="CATERING.STOCK_MOVEMENT.POST",
        )


def test_authorization_adapter_preserves_subject_and_permission():
    evaluator = Mock(return_value=True)

    adapter = CateringAuthorizationAdapter(
        evaluator=evaluator,
    )

    subject = object()
    permission_code = "CATERING.STOCK_TRANSFER.POST"

    assert adapter.authorize(
        subject=subject,
        permission_code=permission_code,
    )

    evaluator.assert_called_once_with(
        subject,
        permission_code,
    )
