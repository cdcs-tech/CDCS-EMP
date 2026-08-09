"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.13.8.9

Authorization decision and execution result governance tests.
"""

from app.core.execution import (
    AuthorizationDecision,
    ExecutionContext,
    ExecutionResult,
)


def build_context():
    """
    Build a valid execution context.
    """

    return ExecutionContext(
        user_id="user-001",
        module_name="test",
        operation="authorization_governance",
        request_id="request-001",
        correlation_id="correlation-001",
        trace_id="trace-001",
        environment="testing",
        metadata={
            "original": True,
        },
    )


def test_allowed_authorization_metadata_is_governance_safe():
    """
    An allowed authorization decision can be represented
    in execution-result governance metadata.
    """

    decision = AuthorizationDecision.allow(
        reason="Permission granted.",
        metadata={
            "permission_code": "test.execute",
            "authorization_source": "AuthorizationEngine",
        },
    )

    context = build_context()

    result = ExecutionResult.success_result(
        data={"value": "completed"},
        message="Execution completed.",
        metadata={
            "authorization_allowed": decision.is_allowed(),
            "authorization_reason": decision.reason,
            "authorization_metadata": dict(
                decision.metadata
            ),
            "user_id": context.user_id,
            "module_name": context.module_name,
            "operation": context.operation,
            "request_id": context.request_id,
            "correlation_id": context.correlation_id,
            "trace_id": context.trace_id,
        },
    )

    assert result.is_success()

    assert result.metadata[
        "authorization_allowed"
    ] is True

    assert result.metadata[
        "authorization_reason"
    ] == "Permission granted."

    assert result.metadata[
        "authorization_metadata"
    ][
        "permission_code"
    ] == "test.execute"

    assert result.metadata[
        "authorization_metadata"
    ][
        "authorization_source"
    ] == "AuthorizationEngine"

    assert result.metadata[
        "user_id"
    ] == "user-001"


def test_denied_authorization_metadata_is_preserved():
    """
    A denied authorization decision can be represented
    without losing its governance information.
    """

    decision = AuthorizationDecision.deny(
        reason="Permission denied.",
        metadata={
            "permission_code": "test.execute",
            "authorization_source": "AuthorizationEngine",
        },
    )

    result = ExecutionResult.failure_result(
        message="Command execution was not authorized.",
        error_code="AUTHORIZATION_DENIED",
        metadata={
            "authorization_allowed": decision.is_allowed(),
            "authorization_reason": decision.reason,
            "authorization_metadata": dict(
                decision.metadata
            ),
        },
    )

    assert result.is_failure()

    assert result.error_code == (
        "AUTHORIZATION_DENIED"
    )

    assert result.metadata[
        "authorization_allowed"
    ] is False

    assert result.metadata[
        "authorization_reason"
    ] == "Permission denied."

    assert result.metadata[
        "authorization_metadata"
    ][
        "permission_code"
    ] == "test.execute"


def test_authorization_metadata_does_not_mutate_decision():
    """
    Execution-result governance metadata must be copied
    rather than mutating the authorization decision.
    """

    decision = AuthorizationDecision.allow(
        reason="Permission granted.",
        metadata={
            "permission_code": "test.execute",
        },
    )

    authorization_metadata = dict(
        decision.metadata
    )

    result = ExecutionResult.success_result(
        metadata={
            "authorization_metadata": authorization_metadata,
        },
    )

    result.metadata[
        "authorization_metadata"
    ][
        "additional"
    ] = True

    assert "additional" not in (
        decision.metadata
    )

def test_governance_builds_success_result():
    """
    Governance service creates a successful execution
    result from an allowed authorization decision.
    """

    from app.core.execution import (
        AuthorizationResultGovernance,
    )

    decision = AuthorizationDecision.allow(
        reason="Permission granted.",
        metadata={
            "permission_code": "test.execute",
        },
    )

    result = AuthorizationResultGovernance.success_result(
        decision,
        context=build_context(),
        data={"completed": True},
        message="Operation completed.",
    )

    assert result.is_success()

    assert result.data == {
        "completed": True
    }

    assert result.metadata[
        "authorization_allowed"
    ] is True

    assert result.metadata[
        "authorization_reason"
    ] == "Permission granted."

    assert result.metadata[
        "authorization_metadata"
    ][
        "permission_code"
    ] == "test.execute"

    assert result.metadata[
        "user_id"
    ] == "user-001"


def test_governance_builds_authorization_failure_result():
    """
    Governance service creates an authorization failure
    result from a denied authorization decision.
    """

    from app.core.execution import (
        AuthorizationResultGovernance,
    )

    decision = AuthorizationDecision.deny(
        reason="Permission denied.",
        metadata={
            "permission_code": "test.execute",
        },
    )

    result = AuthorizationResultGovernance.failure_result(
        decision,
        context=build_context(),
    )

    assert result.is_failure()

    assert result.error_code == (
        "AUTHORIZATION_DENIED"
    )

    assert result.metadata[
        "authorization_allowed"
    ] is False

    assert result.metadata[
        "authorization_reason"
    ] == "Permission denied."

    assert result.metadata[
        "user_id"
    ] == "user-001"


def test_governance_rejects_inconsistent_success_result():
    """
    A denied authorization decision cannot produce
    a successful execution result.
    """

    from app.core.execution import (
        AuthorizationResultGovernance,
    )

    decision = AuthorizationDecision.deny(
        reason="Permission denied."
    )

    try:
        AuthorizationResultGovernance.success_result(
            decision
        )
    except ValueError as exc:
        assert (
            "denied authorization decision"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Expected ValueError."
        )


def test_governance_rejects_inconsistent_failure_result():
    """
    An allowed authorization decision cannot produce
    an authorization failure result.
    """

    from app.core.execution import (
        AuthorizationResultGovernance,
    )

    decision = AuthorizationDecision.allow(
        reason="Permission granted."
    )

    try:
        AuthorizationResultGovernance.failure_result(
            decision
        )
    except ValueError as exc:
        assert (
            "allowed authorization decision"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Expected ValueError."
        )
