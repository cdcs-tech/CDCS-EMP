"""
Tests for reporting permission definitions and mapping.
"""

import pytest

from app.core.reporting.authorization import (
    ReportAuthorizationOperation,
)

from app.core.reporting.permissions import (
    ReportPermissionCode,
    all_report_permissions,
    permission_code_for_operation,
    permission_for_operation,
    register_report_permissions,
    report_permission_mapping,
)

from app.core.security.module import (
    ModulePermission,
)

from app.core.security.permissions import (
    Permission,
)

from app.core.security.registry import (
    PermissionRegistry,
)


def test_report_permission_codes_follow_enterprise_convention():
    """
    Reporting permission codes follow the standard
    module.resource.action convention.
    """

    assert ReportPermissionCode.VIEW == (
        "reporting.report.view"
    )

    assert ReportPermissionCode.EXECUTE == (
        "reporting.report.execute"
    )

    assert ReportPermissionCode.EXPORT == (
        "reporting.report.export"
    )

    assert ReportPermissionCode.MANAGE == (
        "reporting.report.manage"
    )


def test_all_report_permissions_returns_all_supported_operations():
    """
    Every reporting authorization operation has a canonical
    permission definition.
    """

    permissions = all_report_permissions()

    assert len(permissions) == 4

    assert all(
        isinstance(
            permission,
            ModulePermission,
        )
        for permission in permissions
    )


@pytest.mark.parametrize(
    (
        "operation",
        "expected_code",
    ),
    [
        (
            ReportAuthorizationOperation.VIEW,
            "reporting.report.view",
        ),
        (
            ReportAuthorizationOperation.EXECUTE,
            "reporting.report.execute",
        ),
        (
            ReportAuthorizationOperation.EXPORT,
            "reporting.report.export",
        ),
        (
            ReportAuthorizationOperation.MANAGE,
            "reporting.report.manage",
        ),
    ],
)
def test_permission_for_operation_returns_canonical_permission(
    operation,
    expected_code,
):
    """
    Each authorization operation resolves to the expected
    reporting permission.
    """

    permission = permission_for_operation(
        operation
    )

    assert isinstance(
        permission,
        ModulePermission,
    )

    assert isinstance(
        permission,
        Permission,
    )

    assert permission.code == expected_code

    assert permission.module == "reporting"

    assert permission.resource == "report"

    assert permission.action == operation.value


@pytest.mark.parametrize(
    (
        "operation",
        "expected_code",
    ),
    [
        (
            ReportAuthorizationOperation.VIEW,
            "reporting.report.view",
        ),
        (
            "view",
            "reporting.report.view",
        ),
        (
            " VIEW ",
            "reporting.report.view",
        ),
        (
            ReportAuthorizationOperation.EXECUTE,
            "reporting.report.execute",
        ),
        (
            "execute",
            "reporting.report.execute",
        ),
        (
            " export ",
            "reporting.report.export",
        ),
        (
            ReportAuthorizationOperation.MANAGE,
            "reporting.report.manage",
        ),
    ],
)
def test_permission_code_for_operation_normalizes_operation(
    operation,
    expected_code,
):
    """
    Permission code resolution accepts both enum and string
    operation representations.
    """

    assert permission_code_for_operation(
        operation
    ) == expected_code


def test_permission_for_operation_rejects_invalid_operation():
    """
    Invalid authorization operations are rejected.
    """

    with pytest.raises(
        ValueError,
        match="operation is invalid",
    ):
        permission_for_operation(
            "delete"
        )


def test_permission_for_operation_rejects_empty_operation():
    """
    Empty authorization operations are rejected.
    """

    with pytest.raises(
        ValueError,
        match="operation is required",
    ):
        permission_for_operation(
            "   "
        )


def test_permission_mapping_contains_all_operations():
    """
    The canonical permission mapping contains exactly the
    supported reporting authorization operations.
    """

    mapping = report_permission_mapping()

    assert set(mapping) == {
        ReportAuthorizationOperation.VIEW,
        ReportAuthorizationOperation.EXECUTE,
        ReportAuthorizationOperation.EXPORT,
        ReportAuthorizationOperation.MANAGE,
    }


def test_permission_mapping_returns_canonical_codes():
    """
    The permission mapping exposes canonical permission codes.
    """

    mapping = report_permission_mapping()

    assert mapping[
        ReportAuthorizationOperation.VIEW
    ] == "reporting.report.view"

    assert mapping[
        ReportAuthorizationOperation.EXECUTE
    ] == "reporting.report.execute"

    assert mapping[
        ReportAuthorizationOperation.EXPORT
    ] == "reporting.report.export"

    assert mapping[
        ReportAuthorizationOperation.MANAGE
    ] == "reporting.report.manage"


def test_permission_mapping_returns_independent_dictionary():
    """
    The permission mapping returns a new dictionary rather
    than exposing internal mutable state.
    """

    mapping = report_permission_mapping()

    mapping[
        ReportAuthorizationOperation.VIEW
    ] = "changed"

    fresh_mapping = report_permission_mapping()

    assert fresh_mapping[
        ReportAuthorizationOperation.VIEW
    ] == "reporting.report.view"


def test_register_report_permissions_uses_supplied_registry():
    """
    Reporting permissions are registered into the supplied
    enterprise PermissionRegistry.
    """

    registry = PermissionRegistry()

    permissions = register_report_permissions(
        registry
    )

    assert len(permissions) == 4

    assert registry.count() == 4

    assert registry.exists(
        "reporting.report.view"
    )

    assert registry.exists(
        "reporting.report.execute"
    )

    assert registry.exists(
        "reporting.report.export"
    )

    assert registry.exists(
        "reporting.report.manage"
    )


def test_register_report_permissions_registers_expected_objects():
    """
    Registered reporting permissions remain ModulePermission
    instances within the enterprise security registry.
    """

    registry = PermissionRegistry()

    register_report_permissions(
        registry
    )

    permission = registry.get(
        "reporting.report.view"
    )

    assert isinstance(
        permission,
        ModulePermission,
    )

    assert permission.module == "reporting"

    assert permission.resource == "report"

    assert permission.action == "view"


def test_register_report_permissions_does_not_use_global_registry():
    """
    Registration is isolated to the explicitly supplied registry.
    """

    first_registry = PermissionRegistry()

    second_registry = PermissionRegistry()

    register_report_permissions(
        first_registry
    )

    assert first_registry.count() == 4

    assert second_registry.count() == 0


def test_register_report_permissions_rejects_invalid_registry():
    """
    Registration requires an enterprise PermissionRegistry.
    """

    with pytest.raises(
        TypeError,
        match="registry must be a PermissionRegistry",
    ):
        register_report_permissions(
            object()
        )


def test_report_permissions_are_unique():
    """
    Reporting permission codes are unique.
    """

    permissions = all_report_permissions()

    codes = [
        permission.code
        for permission in permissions
    ]

    assert len(codes) == len(set(codes))


def test_report_permissions_match_operation_actions():
    """
    Permission actions correspond exactly to authorization
    operation codes.
    """

    for operation in ReportAuthorizationOperation:

        permission = permission_for_operation(
            operation
        )

        assert permission.action == (
            operation.code
        )


def test_report_permission_definitions_are_provider_neutral():
    """
    Reporting permissions contain no provider-specific
    execution or persistence information.
    """

    for permission in all_report_permissions():

        assert permission.module == "reporting"

        assert permission.resource == "report"

        assert permission.action in {
            "view",
            "execute",
            "export",
            "manage",
        }


def test_report_permission_definitions_have_human_readable_names():
    """
    Canonical reporting permissions expose useful display names.
    """

    permissions = {
        permission.code: permission
        for permission in all_report_permissions()
    }

    assert permissions[
        "reporting.report.view"
    ].name == "View Report"

    assert permissions[
        "reporting.report.execute"
    ].name == "Execute Report"

    assert permissions[
        "reporting.report.export"
    ].name == "Export Report"

    assert permissions[
        "reporting.report.manage"
    ].name == "Manage Report"
