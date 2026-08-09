"""
Command type tests.
"""

from app.core.execution import (
    CommandType,
)


def test_command_types():

    assert (
        CommandType.CREATE.value
        == "create"
    )

    assert (
        CommandType.READ.value
        == "read"
    )

    assert (
        CommandType.UPDATE.value
        == "update"
    )

    assert (
        CommandType.DELETE.value
        == "delete"
    )

    assert (
        CommandType.EXECUTE.value
        == "execute"
    )


def test_command_type_members():

    assert (
        len(CommandType)
        == 5
    )
