"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Application Execution Framework

Execution exceptions.
"""


class ExecutionException(Exception):
    """
    Base exception for execution framework errors.
    """


class ExecutionContractException(
    ExecutionException
):
    """
    Raised when an execution contract is invalid.
    """


class ExecutionContextException(
    ExecutionException
):
    """
    Raised when an execution context is invalid.
    """


class ExecutionResultException(
    ExecutionException
):
    """
    Raised when an execution result is invalid.
    """


class CommandException(
    ExecutionException
):
    """
    Base exception for command errors.
    """


class CommandValidationException(
    CommandException
):
    """
    Raised when a command is invalid.
    """


class HandlerException(
    ExecutionException
):
    """
    Base exception for handler errors.
    """


class HandlerContractException(
    HandlerException
):
    """
    Raised when a handler violates its contract.
    """


__all__ = [
    "ExecutionException",
    "ExecutionContractException",
    "ExecutionContextException",
    "ExecutionResultException",
    "CommandException",
    "CommandValidationException",
    "HandlerException",
    "HandlerContractException",
]
