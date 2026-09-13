from unittest.mock import Mock

from app.core.execution.context import (
    ExecutionContext,
)

from app.core.execution.results import (
    ExecutionResult,
)

from app.modules.procurement.commands import (
    ApprovePurchaseRequestCommand,
    SubmitPurchaseRequestCommand,
)

from app.modules.procurement.handlers import (
    ApprovePurchaseRequestHandler,
    SubmitPurchaseRequestHandler,
)


def _context(operation: str) -> ExecutionContext:
    return ExecutionContext(
        operation=operation,
    )


def _purchase_request(
    status: str,
    request_id: int = 1,
):
    return Mock(
        id=request_id,
        status=status,
    )


def test_submit_handler_supports_submit_command():
    handler = SubmitPurchaseRequestHandler(
        service=Mock()
    )

    command = SubmitPurchaseRequestCommand(
        purchase_request_id=1
    )

    assert handler.supports(command) is True


def test_approve_handler_supports_approve_command():
    handler = ApprovePurchaseRequestHandler(
        service=Mock()
    )

    command = ApprovePurchaseRequestCommand(
        purchase_request_id=1
    )

    assert handler.supports(command) is True


def test_submit_handler_moves_draft_to_submitted():
    service = Mock()

    purchase_request = _purchase_request(
        "DRAFT"
    )

    service.get.return_value = (
        purchase_request
    )

    handler = SubmitPurchaseRequestHandler(
        service=service
    )

    result = handler.handle(
        SubmitPurchaseRequestCommand(1),
        _context(
            "purchase_request.submit"
        ),
    )

    assert isinstance(
        result,
        ExecutionResult,
    )
    assert result.success is True
    assert purchase_request.status == "SUBMITTED"

    service.get.assert_called_once_with(1)
    service.update.assert_called_once_with(
        purchase_request
    )


def test_submit_handler_rejects_non_draft():
    service = Mock()

    purchase_request = _purchase_request(
        "SUBMITTED"
    )

    service.get.return_value = (
        purchase_request
    )

    handler = SubmitPurchaseRequestHandler(
        service=service
    )

    result = handler.handle(
        SubmitPurchaseRequestCommand(1),
        _context(
            "purchase_request.submit"
        ),
    )

    assert result.success is False
    assert (
        result.error_code
        == "INVALID_PURCHASE_REQUEST_STATE"
    )
    assert purchase_request.status == "SUBMITTED"
    service.update.assert_not_called()


def test_approve_handler_moves_submitted_to_approved():
    service = Mock()

    purchase_request = _purchase_request(
        "SUBMITTED"
    )

    service.get.return_value = (
        purchase_request
    )

    handler = ApprovePurchaseRequestHandler(
        service=service
    )

    result = handler.handle(
        ApprovePurchaseRequestCommand(1),
        _context(
            "purchase_request.approve"
        ),
    )

    assert isinstance(
        result,
        ExecutionResult,
    )
    assert result.success is True
    assert purchase_request.status == "APPROVED"

    service.get.assert_called_once_with(1)
    service.update.assert_called_once_with(
        purchase_request
    )


def test_approve_handler_rejects_non_submitted():
    service = Mock()

    purchase_request = _purchase_request(
        "DRAFT"
    )

    service.get.return_value = (
        purchase_request
    )

    handler = ApprovePurchaseRequestHandler(
        service=service
    )

    result = handler.handle(
        ApprovePurchaseRequestCommand(1),
        _context(
            "purchase_request.approve"
        ),
    )

    assert result.success is False
    assert (
        result.error_code
        == "INVALID_PURCHASE_REQUEST_STATE"
    )
    assert purchase_request.status == "DRAFT"
    service.update.assert_not_called()


def test_submit_handler_does_not_authorize_directly():
    service = Mock()

    purchase_request = _purchase_request(
        "DRAFT"
    )

    service.get.return_value = (
        purchase_request
    )

    handler = SubmitPurchaseRequestHandler(
        service=service
    )

    result = handler.handle(
        SubmitPurchaseRequestCommand(1),
        _context(
            "purchase_request.submit"
        ),
    )

    assert result.success is True
    assert not hasattr(
        handler,
        "authorize",
    )


def test_approve_handler_does_not_authorize_directly():
    service = Mock()

    purchase_request = _purchase_request(
        "SUBMITTED"
    )

    service.get.return_value = (
        purchase_request
    )

    handler = ApprovePurchaseRequestHandler(
        service=service
    )

    result = handler.handle(
        ApprovePurchaseRequestCommand(1),
        _context(
            "purchase_request.approve"
        ),
    )

    assert result.success is True
    assert not hasattr(
        handler,
        "authorize",
    )


def test_handlers_return_purchase_request_data():
    service = Mock()

    purchase_request = _purchase_request(
        "DRAFT"
    )

    service.get.return_value = (
        purchase_request
    )

    handler = SubmitPurchaseRequestHandler(
        service=service
    )

    result = handler.handle(
        SubmitPurchaseRequestCommand(1),
        _context(
            "purchase_request.submit"
        ),
    )

    assert result.success is True
    assert result.data is purchase_request
    assert (
        result.metadata["previous_status"]
        == "DRAFT"
    )
    assert (
        result.metadata["new_status"]
        == "SUBMITTED"
    )
