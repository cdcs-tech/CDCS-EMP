"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure Tests

Enterprise exception tests.
"""

import pytest

from app.core.platform import (
    CDCSPlatformException,
    PlatformConfigurationException,
    PlatformRuntimeException,
    PlatformContextException,
    PlatformServiceException,
    PlatformInfrastructureException,
)


def test_base_platform_exception():

    exception = CDCSPlatformException(
        "Platform failure"
    )

    assert (
        str(exception)
        == "Platform failure"
    )

    assert (
        exception.error_code
        == "PLATFORM_ERROR"
    )


def test_platform_exception_to_dict():

    exception = CDCSPlatformException(
        "Platform failure",
        details={
            "component": "test",
        },
    )

    data = exception.to_dict()

    assert (
        data["error_code"]
        == "PLATFORM_ERROR"
    )

    assert (
        data["message"]
        == "Platform failure"
    )

    assert (
        data["details"]["component"]
        == "test"
    )


def test_custom_error_code():

    exception = CDCSPlatformException(
        "Custom failure",
        error_code="CUSTOM_ERROR",
    )

    assert (
        exception.error_code
        == "CUSTOM_ERROR"
    )


@pytest.mark.parametrize(
    "exception_class,error_code",
    [
        (
            PlatformConfigurationException,
            "PLATFORM_CONFIGURATION_ERROR",
        ),
        (
            PlatformRuntimeException,
            "PLATFORM_RUNTIME_ERROR",
        ),
        (
            PlatformContextException,
            "PLATFORM_CONTEXT_ERROR",
        ),
        (
            PlatformServiceException,
            "PLATFORM_SERVICE_ERROR",
        ),
        (
            PlatformInfrastructureException,
            "PLATFORM_INFRASTRUCTURE_ERROR",
        ),
    ],
)
def test_platform_exception_hierarchy(
    exception_class,
    error_code,
):

    exception = exception_class(
        "Test platform error"
    )

    assert isinstance(
        exception,
        CDCSPlatformException,
    )

    assert (
        exception.error_code
        == error_code
    )


def test_empty_message_uses_class_name():

    exception = (
        PlatformServiceException()
    )

    assert (
        exception.message
        == "PlatformServiceException"
    )


def test_exception_details_are_copied():

    details = {
        "module": "platform",
        "operation": "test",
    }

    exception = CDCSPlatformException(
        "Failure",
        details=details,
    )

    details["module"] = "changed"

    assert (
        exception.details["module"]
        == "platform"
    )


def test_exception_repr():

    exception = (
        PlatformInfrastructureException(
            "Infrastructure failure"
        )
    )

    representation = repr(
        exception
    )

    assert (
        "PlatformInfrastructureException"
        in representation
    )

    assert (
        "PLATFORM_INFRASTRUCTURE_ERROR"
        in representation
    )


def test_exception_can_be_raised():

    with pytest.raises(
        PlatformContextException
    ):

        raise PlatformContextException(
            "Context failure"
        )
