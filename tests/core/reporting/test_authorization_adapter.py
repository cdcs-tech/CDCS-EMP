"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting & Analytics Framework

Tests for the reporting authorization adapter.
"""

import pytest

from app.core.reporting.authorization import (
    ReportAuthorizationContext,
    ReportAuthorizationDecision,
    ReportAuthorizationRequest,
    ReportAuthorizationResource,
    ReportAuthorizationSubject,
)
from app.core.reporting.authorization_adapter import (
    ReportingAuthorizationAdapter,
)


def make_request(
    operation="execute",
):
    return ReportAuthorizationRequest(
        subject=ReportAuthorizationSubject(
            identifier="user-001",
        ),
        operation=operation,
        resource=ReportAuthorizationResource(
            resource_type="report",
            identifier="sales.monthly",
        ),
        context=ReportAuthorizationContext(
            metadata={
                "module": "reporting",
            },
        ),
    )


def test_adapter_requires_callable_evaluator():
    with pytest.raises(
        ValueError,
        match="callable evaluator",
    ):
        ReportingAuthorizationAdapter(
            evaluator=None,
        )


def test_adapter_requires_authorization_request():
    adapter = ReportingAuthorizationAdapter(
        evaluator=lambda request, permission: True,
    )

    with pytest.raises(
        ValueError,
        match="ReportAuthorizationRequest",
    ):
        adapter.authorize("invalid")


def test_adapter_resolves_execute_permission():
    adapter = ReportingAuthorizationAdapter(
        evaluator=lambda request, permission: True,
    )

    assert (
        adapter.permission_for(
            make_request("execute")
        )
        == "reporting.report.execute"
    )


@pytest.mark.parametrize(
    "operation,expected",
    [
        (
            "view",
            "reporting.report.view",
        ),
        (
            "execute",
            "reporting.report.execute",
        ),
        (
            "export",
            "reporting.report.export",
        ),
        (
            "manage",
            "reporting.report.manage",
        ),
    ],
)
def test_adapter_resolves_all_reporting_permissions(
    operation,
    expected,
):
    adapter = ReportingAuthorizationAdapter(
        evaluator=lambda request, permission: True,
    )

    assert (
        adapter.permission_for(
            make_request(operation)
        )
        == expected
    )


def test_adapter_passes_request_and_permission_to_evaluator():
    calls = []

    def evaluator(
        request,
        permission_code,
    ):
        calls.append(
            (
                request,
                permission_code,
            )
        )

        return True

    adapter = ReportingAuthorizationAdapter(
        evaluator=evaluator,
    )

    request = make_request("export")

    decision = adapter.authorize(
        request
    )

    assert decision.is_allowed is True

    assert calls == [
        (
            request,
            "reporting.report.export",
        )
    ]


def test_adapter_converts_true_result_to_allow_decision():
    adapter = ReportingAuthorizationAdapter(
        evaluator=lambda request, permission: True,
    )

    decision = adapter.authorize(
        make_request()
    )

    assert isinstance(
        decision,
        ReportAuthorizationDecision,
    )

    assert decision.is_allowed is True
    assert decision.is_denied is False
    assert decision.reason == (
        "Reporting authorization granted."
    )

    assert decision.metadata == {
        "permission_code":
            "reporting.report.execute",
    }


def test_adapter_converts_false_result_to_deny_decision():
    adapter = ReportingAuthorizationAdapter(
        evaluator=lambda request, permission: False,
    )

    decision = adapter.authorize(
        make_request()
    )

    assert isinstance(
        decision,
        ReportAuthorizationDecision,
    )

    assert decision.is_allowed is False
    assert decision.is_denied is True
    assert decision.reason == (
        "Reporting authorization denied."
    )

    assert decision.metadata == {
        "permission_code":
            "reporting.report.execute",
    }


def test_adapter_preserves_existing_decision():
    expected = ReportAuthorizationDecision(
        status="deny",
        reason="Policy denied access.",
        metadata={
            "source": "security",
        },
    )

    adapter = ReportingAuthorizationAdapter(
        evaluator=lambda request, permission: expected,
    )

    decision = adapter.authorize(
        make_request()
    )

    assert decision is expected


def test_adapter_wraps_evaluator_failure():
    def evaluator(
        request,
        permission_code,
    ):
        raise RuntimeError(
            "security failure"
        )

    adapter = ReportingAuthorizationAdapter(
        evaluator=evaluator,
    )

    with pytest.raises(
        RuntimeError,
        match="Reporting authorization evaluation failed",
    ):
        adapter.authorize(
            make_request()
        )


def test_adapter_rejects_invalid_evaluator_result():
    adapter = ReportingAuthorizationAdapter(
        evaluator=lambda request, permission: "allow",
    )

    with pytest.raises(
        RuntimeError,
        match="must return a boolean",
    ):
        adapter.authorize(
            make_request()
        )
