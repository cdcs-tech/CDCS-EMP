"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting & Analytics Framework

Reporting permission definitions and permission mapping.
"""

from __future__ import annotations

from app.core.reporting.authorization import (
    ReportAuthorizationOperation,
)
from app.core.security.module import (
    ModulePermission,
)
from app.core.security.registry import (
    PermissionRegistry,
)


class ReportPermissionCode:
    """
    Canonical reporting permission codes.

    Reporting permissions follow the enterprise security
    convention:

        module.resource.action

    The reporting module therefore uses:

        reporting.report.<operation>
    """

    VIEW = "reporting.report.view"

    EXECUTE = "reporting.report.execute"

    EXPORT = "reporting.report.export"

    MANAGE = "reporting.report.manage"


_REPORT_PERMISSION_DEFINITIONS: dict[
    ReportAuthorizationOperation,
    ModulePermission,
] = {
    ReportAuthorizationOperation.VIEW: ModulePermission(
        module="reporting",
        resource="report",
        action="view",
        name="View Report",
        description=(
            "Permission to view reporting resources."
        ),
    ),
    ReportAuthorizationOperation.EXECUTE: ModulePermission(
        module="reporting",
        resource="report",
        action="execute",
        name="Execute Report",
        description=(
            "Permission to execute reporting resources."
        ),
    ),
    ReportAuthorizationOperation.EXPORT: ModulePermission(
        module="reporting",
        resource="report",
        action="export",
        name="Export Report",
        description=(
            "Permission to export reporting resources."
        ),
    ),
    ReportAuthorizationOperation.MANAGE: ModulePermission(
        module="reporting",
        resource="report",
        action="manage",
        name="Manage Report",
        description=(
            "Permission to manage reporting resources."
        ),
    ),
}


def permission_for_operation(
    operation: (
        ReportAuthorizationOperation
        | str
    ),
) -> ModulePermission:
    """
    Resolve the canonical reporting permission for an
    authorization operation.

    Args:
        operation:
            Reporting authorization operation or its string
            representation.

    Returns:
        ModulePermission:
            The canonical reporting permission definition.

    Raises:
        ValueError:
            When the supplied operation is invalid.
    """

    normalized_operation = (
        ReportAuthorizationOperation.normalize(
            operation
        )
    )

    return _REPORT_PERMISSION_DEFINITIONS[
        normalized_operation
    ]


def permission_code_for_operation(
    operation: (
        ReportAuthorizationOperation
        | str
    ),
) -> str:
    """
    Resolve the canonical permission code for an
    authorization operation.

    Args:
        operation:
            Reporting authorization operation or its string
            representation.

    Returns:
        str:
            Canonical reporting permission code.
    """

    return permission_for_operation(
        operation
    ).code


def all_report_permissions() -> tuple[
    ModulePermission,
    ...,
]:
    """
    Return all canonical reporting permissions.

    Registration order follows the reporting authorization
    operation definition order.
    """

    return tuple(
        _REPORT_PERMISSION_DEFINITIONS.values()
    )


def register_report_permissions(
    registry: PermissionRegistry,
) -> tuple[ModulePermission, ...]:
    """
    Register all canonical reporting permissions in the
    supplied enterprise permission registry.

    The supplied registry is deliberately used instead of
    implicitly depending on the global security registry.

    Args:
        registry:
            Enterprise permission registry.

    Returns:
        tuple[ModulePermission, ...]:
            The permissions registered.

    Raises:
        TypeError:
            When an invalid registry is supplied.
    """

    if not isinstance(
        registry,
        PermissionRegistry,
    ):
        raise TypeError(
            "registry must be a PermissionRegistry."
        )

    permissions = all_report_permissions()

    for permission in permissions:

        registry.register(
            permission
        )

    return permissions


def report_permission_mapping() -> dict[
    ReportAuthorizationOperation,
    str,
]:
    """
    Return the canonical mapping between reporting
    authorization operations and permission codes.

    The returned mapping is a copy and can therefore be
    safely modified by the caller.
    """

    return {
        operation: permission.code
        for operation, permission
        in _REPORT_PERMISSION_DEFINITIONS.items()
    }


__all__ = [
    "ReportPermissionCode",
    "permission_for_operation",
    "permission_code_for_operation",
    "all_report_permissions",
    "register_report_permissions",
    "report_permission_mapping",
]
