"""
Use-case execution tests.
"""

import pytest

from app.core.execution import (
    BaseCommand,
    BaseCommandHandler,
    BaseUseCase,
    CommandDispatcher,
    CommandRegistry,
    ExecutionContext,
    ExecutionContractException,
    ExecutionResult,
    UseCaseExecutor,
)


class CreateInvoiceCommand(
    BaseCommand
):

    command_name = (
        "finance.create_invoice"
    )

    def __init__(
        self,
        amount: float,
    ):
        self.amount = amount

    def execute_name(self) -> str:

        return self.command_name


class CreateInvoiceHandler(
    BaseCommandHandler
):

    command_type = (
        CreateInvoiceCommand
    )

    def handle(
        self,
        command,
        context,
    ):

        return ExecutionResult.success_result(
            data={
                "invoice_created": True,
                "amount": command.amount,
            },
            message="Invoice created.",
        )


class CreateInvoiceUseCase(
    BaseUseCase
):

    use_case_name = (
        "finance.create_invoice"
    )

    command_type = (
        CreateInvoiceCommand
    )

    def build_command(
        self,
        **kwargs,
    ):

        return CreateInvoiceCommand(
            amount=kwargs[
                "amount"
            ]
        )


class InvalidUseCase(
    BaseUseCase
):

    use_case_name = (
        "finance.invalid"
    )

    command_type = (
        CreateInvoiceCommand
    )

    def build_command(
        self,
        **kwargs,
    ):

        return "invalid-command"


def build_executor():

    registry = CommandRegistry()

    registry.register(
        CreateInvoiceCommand
    )

    dispatcher = CommandDispatcher(
        registry=registry
    )

    dispatcher.register_handler(
        CreateInvoiceHandler()
    )

    return UseCaseExecutor(
        dispatcher=dispatcher
    )


def build_context():

    return ExecutionContext(
        user_id="user-001",
        module_name="finance",
        operation="create_invoice",
        request_id="req-001",
    )


def test_use_case_contract():

    use_case = (
        CreateInvoiceUseCase()
    )

    use_case.validate()


def test_use_case_builds_command():

    use_case = (
        CreateInvoiceUseCase()
    )

    command = use_case.build_command(
        amount=250.0
    )

    assert isinstance(
        command,
        CreateInvoiceCommand,
    )

    assert (
        command.amount
        == 250.0
    )


def test_use_case_execution():

    executor = build_executor()

    use_case = (
        CreateInvoiceUseCase()
    )

    result = (
        executor.execute_use_case(
            use_case,
            build_context(),
            amount=250.0,
        )
    )

    assert result.is_success()

    assert (
        result.data[
            "invoice_created"
        ]
        is True
    )

    assert (
        result.data[
            "amount"
        ]
        == 250.0
    )


def test_use_case_execute_method():

    executor = build_executor()

    use_case = (
        CreateInvoiceUseCase()
    )

    result = use_case.execute(
        executor,
        build_context(),
        amount=500.0,
    )

    assert result.is_success()

    assert (
        result.data[
            "amount"
        ]
        == 500.0
    )


def test_use_case_context_preparation():

    class MetadataUseCase(
        CreateInvoiceUseCase
    ):

        def prepare_context(
            self,
            context,
        ):

            return context.with_metadata(
                use_case=(
                    self.use_case_name
                )
            )

    executor = build_executor()

    use_case = (
        MetadataUseCase()
    )

    context = build_context()

    prepared = (
        use_case.prepare_context(
            context
        )
    )

    assert (
        prepared.metadata[
            "use_case"
        ]
        == "finance.create_invoice"
    )

    result = use_case.execute(
        executor,
        context,
        amount=100.0,
    )

    assert result.is_success()


def test_invalid_use_case_command_fails():

    executor = build_executor()

    use_case = (
        InvalidUseCase()
    )

    with pytest.raises(
        ExecutionContractException
    ):

        executor.execute_use_case(
            use_case,
            build_context(),
        )


def test_invalid_use_case_type_fails():

    class InvalidUseCaseType:

        pass

    executor = build_executor()

    with pytest.raises(
        ExecutionContractException
    ):

        executor.execute_use_case(
            InvalidUseCaseType(),
            build_context(),
        )


def test_invalid_command_type_contract_fails():

    class InvalidCommandTypeUseCase(
        BaseUseCase
    ):

        use_case_name = (
            "finance.invalid_type"
        )

        command_type = str

        def build_command(
            self,
            **kwargs,
        ):

            return CreateInvoiceCommand(
                amount=100.0
            )

    use_case = (
        InvalidCommandTypeUseCase()
    )

    with pytest.raises(
        ExecutionContractException
    ):

        use_case.validate()


def test_invalid_context_fails():

    executor = build_executor()

    use_case = (
        CreateInvoiceUseCase()
    )

    with pytest.raises(
        ExecutionContractException
    ):

        executor.execute_use_case(
            use_case,
            "invalid-context",
            amount=100.0,
        )


def test_use_case_executor_creation():

    executor = build_executor()

    assert (
        executor.dispatcher
        is not None
    )
