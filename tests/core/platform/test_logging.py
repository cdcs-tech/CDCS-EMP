"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure Tests

Platform logging tests.
"""

import logging

from app.core.platform import (
    PlatformConfig,
    PlatformLogger,
    RequestContext,
    RuntimeContext,
)


def create_context():

    runtime = RuntimeContext(
        config=PlatformConfig(
            environment="testing",
            testing=True,
        )
    )

    return RequestContext(
        runtime=runtime,
        user_id="user-001",
        module_name="finance",
        operation="create",
    )


def test_platform_logger_creation():

    logger = PlatformLogger(
        "test_logger"
    )

    assert (
        logger.logger.name
        == "test_logger"
    )


def test_logger_debug():

    logger = PlatformLogger(
        "test_debug"
    )

    logger.set_level(
        logging.DEBUG
    )

    logger.debug(
        "Debug message"
    )

    assert (
        logger.get_level()
        == logging.DEBUG
    )


def test_logger_info():

    logger = PlatformLogger(
        "test_info"
    )

    logger.info(
        "Information message"
    )

    assert (
        logger.logger.name
        == "test_info"
    )


def test_logger_warning():

    logger = PlatformLogger(
        "test_warning"
    )

    logger.warning(
        "Warning message"
    )

    assert (
        logger.logger.name
        == "test_warning"
    )


def test_logger_error():

    logger = PlatformLogger(
        "test_error"
    )

    logger.error(
        "Error message"
    )

    assert (
        logger.logger.name
        == "test_error"
    )


def test_logger_critical():

    logger = PlatformLogger(
        "test_critical"
    )

    logger.critical(
        "Critical message"
    )

    assert (
        logger.logger.name
        == "test_critical"
    )


def test_context_metadata():

    logger = PlatformLogger(
        "test_context"
    )

    context = create_context()

    data = logger._extra(
        context
    )

    assert (
        data["request_id"]
        == context.request_id
    )

    assert (
        data["correlation_id"]
        == context.correlation_id
    )

    assert (
        data["trace_id"]
        == context.trace_id
    )

    assert (
        data["user_id"]
        == "user-001"
    )

    assert (
        data["module_name"]
        == "finance"
    )

    assert (
        data["operation"]
        == "create"
    )


def test_custom_metadata():

    logger = PlatformLogger(
        "test_metadata"
    )

    data = logger._extra(
        None,
        component="platform",
        action="test",
    )

    assert (
        data["component"]
        == "platform"
    )

    assert (
        data["action"]
        == "test"
    )


def test_context_and_custom_metadata():

    logger = PlatformLogger(
        "test_combined"
    )

    context = create_context()

    data = logger._extra(
        context,
        component="platform",
        action="test",
    )

    assert (
        data["request_id"]
        == context.request_id
    )

    assert (
        data["component"]
        == "platform"
    )

    assert (
        data["action"]
        == "test"
    )


def test_logger_level():

    logger = PlatformLogger(
        "test_level"
    )

    logger.set_level(
        logging.WARNING
    )

    assert (
        logger.get_level()
        == logging.WARNING
    )


def test_logger_repr():

    logger = PlatformLogger(
        "test_repr"
    )

    representation = repr(
        logger
    )

    assert (
        "PlatformLogger"
        in representation
    )

    assert (
        "test_repr"
        in representation
    )
