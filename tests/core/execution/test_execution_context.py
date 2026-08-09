"""
Execution context tests.
"""

import pytest

from app.core.execution import (
    ExecutionContext,
    ExecutionContextException,
)


def test_context_creation():

    context = ExecutionContext(
        user_id="user-001",
        module_name="finance",
        operation="create_invoice",
        request_id="req-001",
        correlation_id="corr-001",
        trace_id="trace-001",
        environment="testing",
    )

    assert context.user_id == "user-001"
    assert context.module_name == "finance"
    assert context.operation == "create_invoice"

    context.validate()


def test_context_requires_module():

    context = ExecutionContext(
        operation="create_invoice",
    )

    with pytest.raises(
        ExecutionContextException
    ):
        context.validate()


def test_context_requires_operation():

    context = ExecutionContext(
        module_name="finance",
    )

    with pytest.raises(
        ExecutionContextException
    ):
        context.validate()


def test_context_metadata():

    context = ExecutionContext(
        module_name="finance",
        operation="create_invoice",
    )

    updated = context.with_metadata(
        entity_id="INV-001",
        source="api",
    )

    assert (
        updated.metadata["entity_id"]
        == "INV-001"
    )

    assert (
        updated.metadata["source"]
        == "api"
    )
