"""
Execution context integration tests.
"""

from app.core.execution import (
    BaseCommand,
    BaseCommandHandler,
    BaseUseCase,
    CommandDispatcher,
    CommandRegistry,
    ExecutionContext,
    ExecutionContextAdapter,
    ExecutionResult,
    UseCaseExecutor,
)


class ContextCommand(BaseCommand):

    command_name = (
        "test.context_operation"
    )

    def __init__(
        self,
        value: str,
    ):

        self.value = value

    def execute_name(self) -> str:

        return self.command_name


class ContextHandler(
    BaseCommandHandler
):

    command_type = (
        ContextCommand
    )

    captured_context = None

    def handle(
        self,
        command,
        context,
    ):

        self.captured_context = context

        return ExecutionResult.success_result(
            data={
                "value": command.value,
                "metadata": dict(
                    context.metadata
                ),
            }
        )


class ContextUseCase(
    BaseUseCase
):

    use_case_name = (
        "test.context_operation"
    )

    command_type = (
        ContextCommand
    )

    def build_command(
        self,
        **kwargs,
    ):

        return ContextCommand(
            kwargs["value"]
        )


def build_environment():

    registry = CommandRegistry()

    registry.register(
        ContextCommand
    )

    handler = ContextHandler()

    dispatcher = CommandDispatcher(
        registry=registry
    )

    dispatcher.register_handler(
        handler
    )

    executor = UseCaseExecutor(
        dispatcher=dispatcher
    )

    return (
        executor,
        handler,
    )


def build_context():

    return ExecutionContext(
        user_id="user-001",
        module_name="test",
        operation="context_operation",
        request_id="request-001",
        correlation_id="correlation-001",
        trace_id="trace-001",
        environment="testing",
        metadata={
            "original": True,
        },
    )


def build_scoped_context():

    return ExecutionContext(
        user_id="user-001",
        tenant_id="tenant-001",
        organization_id="organization-001",
        module_name="test",
        operation="context_operation",
        request_id="request-001",
        correlation_id="correlation-001",
        trace_id="trace-001",
        environment="testing",
        metadata={
            "original": True,
        },
    )


def test_context_adapter_preserves_original():

    context = build_context()

    enriched = (
        ExecutionContextAdapter.enrich(
            context,
            extra="value",
        )
    )

    assert (
        context.metadata[
            "extra"
        ]
        if "extra" in context.metadata
        else None
    ) is None

    assert (
        enriched.metadata[
            "extra"
        ]
        == "value"
    )

    assert (
        enriched.request_id
        == context.request_id
    )

    assert (
        enriched.correlation_id
        == context.correlation_id
    )

    assert (
        enriched.trace_id
        == context.trace_id
    )


def test_use_case_context_is_enriched():

    executor, handler = (
        build_environment()
    )

    use_case = (
        ContextUseCase()
    )

    result = executor.execute_use_case(
        use_case,
        build_context(),
        value="hello",
    )

    assert result.is_success()

    context = (
        handler.captured_context
    )

    assert (
        context.metadata[
            "use_case"
        ]
        == "test.context_operation"
    )


def test_command_context_is_enriched():

    executor, handler = (
        build_environment()
    )

    use_case = (
        ContextUseCase()
    )

    executor.execute_use_case(
        use_case,
        build_context(),
        value="hello",
    )

    context = (
        handler.captured_context
    )

    assert (
        context.metadata[
            "command"
        ]
        == "test.context_operation"
    )


def test_handler_context_is_enriched():

    executor, handler = (
        build_environment()
    )

    use_case = (
        ContextUseCase()
    )

    executor.execute_use_case(
        use_case,
        build_context(),
        value="hello",
    )

    context = (
        handler.captured_context
    )

    assert (
        "handler"
        in context.metadata
    )

    assert (
        context.metadata[
            "handler"
        ].endswith(
            "ContextHandler"
        )
    )


def test_context_identifiers_are_preserved():

    executor, handler = (
        build_environment()
    )

    original = build_context()

    executor.execute_use_case(
        ContextUseCase(),
        original,
        value="hello",
    )

    context = (
        handler.captured_context
    )

    assert (
        context.user_id
        == original.user_id
    )

    assert (
        context.request_id
        == original.request_id
    )

    assert (
        context.correlation_id
        == original.correlation_id
    )

    assert (
        context.trace_id
        == original.trace_id
    )

    assert (
        context.environment
        == original.environment
    )


def test_context_metadata_is_accumulated():

    executor, handler = (
        build_environment()
    )

    original = build_context()

    executor.execute_use_case(
        ContextUseCase(),
        original,
        value="hello",
    )

    context = (
        handler.captured_context
    )

    assert (
        context.metadata[
            "original"
        ]
        is True
    )

    assert (
        "use_case"
        in context.metadata
    )

    assert (
        "command"
        in context.metadata
    )

    assert (
        "handler"
        in context.metadata
    )


def test_context_validation():

    context = build_context()

    ExecutionContextAdapter.validate(
        context
    )


def test_context_adapter_preserves_tenant_scope():

    context = build_scoped_context()

    enriched = (
        ExecutionContextAdapter.enrich(
            context,
            extra="value",
        )
    )

    assert (
        enriched.tenant_id
        == "tenant-001"
    )

    assert (
        enriched.organization_id
        == "organization-001"
    )


def test_context_adapter_preserves_tenant_scope_through_use_case():

    executor, handler = (
        build_environment()
    )

    context = build_scoped_context()

    executor.execute_use_case(
        ContextUseCase(),
        context,
        value="hello",
    )

    captured = (
        handler.captured_context
    )

    assert (
        captured.tenant_id
        == "tenant-001"
    )

    assert (
        captured.organization_id
        == "organization-001"
    )
