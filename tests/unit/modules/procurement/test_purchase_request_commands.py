from app.core.execution.commands.types import (
    CommandType,
)

from app.modules.procurement.commands import (
    ApprovePurchaseRequestCommand,
    SubmitPurchaseRequestCommand,
)


def test_submit_purchase_request_command_contract():
    command = SubmitPurchaseRequestCommand(
        purchase_request_id=1
    )

    command.validate()

    assert (
        command.command_name
        == "procurement.purchase_request.submit"
    )
    assert command.command_type is CommandType.EXECUTE
    assert (
        command.execute_name()
        == "procurement.purchase_request.submit"
    )
    assert command.payload() == {
        "purchase_request_id": 1
    }


def test_approve_purchase_request_command_contract():
    command = ApprovePurchaseRequestCommand(
        purchase_request_id=1
    )

    command.validate()

    assert (
        command.command_name
        == "procurement.purchase_request.approve"
    )
    assert command.command_type is CommandType.EXECUTE
    assert (
        command.execute_name()
        == "procurement.purchase_request.approve"
    )
    assert command.payload() == {
        "purchase_request_id": 1
    }


def test_submit_command_rejects_non_integer_id():
    command = SubmitPurchaseRequestCommand(
        purchase_request_id="1"
    )

    try:
        command.validate()
    except ValueError as exc:
        assert (
            str(exc)
            == "purchase_request_id must be an integer."
        )
    else:
        raise AssertionError(
            "Expected ValueError."
        )


def test_approve_command_rejects_non_integer_id():
    command = ApprovePurchaseRequestCommand(
        purchase_request_id="1"
    )

    try:
        command.validate()
    except ValueError as exc:
        assert (
            str(exc)
            == "purchase_request_id must be an integer."
        )
    else:
        raise AssertionError(
            "Expected ValueError."
        )


def test_submit_command_rejects_non_positive_id():
    command = SubmitPurchaseRequestCommand(
        purchase_request_id=0
    )

    try:
        command.validate()
    except ValueError as exc:
        assert (
            str(exc)
            == "purchase_request_id must be greater than zero."
        )
    else:
        raise AssertionError(
            "Expected ValueError."
        )


def test_approve_command_rejects_non_positive_id():
    command = ApprovePurchaseRequestCommand(
        purchase_request_id=-1
    )

    try:
        command.validate()
    except ValueError as exc:
        assert (
            str(exc)
            == "purchase_request_id must be greater than zero."
        )
    else:
        raise AssertionError(
            "Expected ValueError."
        )


def test_submit_command_metadata():
    metadata = (
        SubmitPurchaseRequestCommand.metadata
    )

    assert metadata is not None
    assert metadata.name == "Submit Purchase Request"
    assert metadata.module_name == "PROCUREMENT"
    assert metadata.operation == "purchase_request.submit"
    assert metadata.version == "1.0"
    assert metadata.category == "workflow"


def test_approve_command_metadata():
    metadata = (
        ApprovePurchaseRequestCommand.metadata
    )

    assert metadata is not None
    assert metadata.name == "Approve Purchase Request"
    assert metadata.module_name == "PROCUREMENT"
    assert metadata.operation == "purchase_request.approve"
    assert metadata.version == "1.0"
    assert metadata.category == "workflow"
