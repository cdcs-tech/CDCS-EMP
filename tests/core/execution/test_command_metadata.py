"""
Command metadata tests.
"""

import pytest

from app.core.execution import (
    CommandMetadata,
    CommandValidationException,
    validate_command_metadata,
)


def test_metadata_creation():

    metadata = CommandMetadata(
        name="create_invoice",
        module_name="finance",
        operation="create_invoice",
        version="1.0",
        description="Create an invoice.",
        category="transaction",
    )

    assert (
        metadata.name
        == "create_invoice"
    )

    assert (
        metadata.module_name
        == "finance"
    )

    assert (
        metadata.operation
        == "create_invoice"
    )

    assert (
        metadata.version
        == "1.0"
    )


def test_metadata_qualified_name():

    metadata = CommandMetadata(
        name="create_invoice",
        module_name="finance",
        operation="create_invoice",
    )

    assert (
        metadata.qualified_name()
        == "finance.create_invoice"
    )


def test_metadata_validation():

    metadata = CommandMetadata(
        name="create_invoice",
        module_name="finance",
        operation="create_invoice",
    )

    validate_command_metadata(
        metadata
    )


def test_metadata_requires_name():

    metadata = CommandMetadata(
        name="",
        module_name="finance",
        operation="create_invoice",
    )

    with pytest.raises(
        CommandValidationException
    ):

        validate_command_metadata(
            metadata
        )


def test_metadata_requires_module():

    metadata = CommandMetadata(
        name="create_invoice",
        module_name="",
        operation="create_invoice",
    )

    with pytest.raises(
        CommandValidationException
    ):

        validate_command_metadata(
            metadata
        )


def test_metadata_requires_operation():

    metadata = CommandMetadata(
        name="create_invoice",
        module_name="finance",
        operation="",
    )

    with pytest.raises(
        CommandValidationException
    ):

        validate_command_metadata(
            metadata
        )
