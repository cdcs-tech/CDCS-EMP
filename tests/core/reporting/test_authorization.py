"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting & Analytics Framework

Tests for provider-neutral reporting authorization
contracts.
"""

import pytest

from app.core.reporting.authorization import (
    ReportAuthorizationContext,
    ReportAuthorizationDecision,
    ReportAuthorizationDecisionStatus,
    ReportAuthorizationOperation,
    ReportAuthorizationRequest,
    ReportAuthorizationResource,
    ReportAuthorizationSubject,
)


# ---------------------------------------------------------
# Authorization Operation
# ---------------------------------------------------------


@pytest.mark.parametrize(
    "value,expected",
    [
        (
            "view",
            ReportAuthorizationOperation.VIEW,
        ),
        (
            " VIEW ",
            ReportAuthorizationOperation.VIEW,
        ),
        (
            "execute",
            ReportAuthorizationOperation.EXECUTE,
        ),
        (
            "EXPORT",
            ReportAuthorizationOperation.EXPORT,
        ),
        (
            "manage",
            ReportAuthorizationOperation.MANAGE,
        ),
    ],
)
def test_authorization_operation_normalizes_supported_values(
    value,
    expected,
):
    assert (
        ReportAuthorizationOperation.normalize(value)
        is expected
    )


def test_authorization_operation_accepts_enum_instance():
    operation = ReportAuthorizationOperation.VIEW

    assert (
        ReportAuthorizationOperation.normalize(operation)
        is operation
    )


@pytest.mark.parametrize(
    "value",
    [
        "",
        " ",
        "unsupported",
        "delete",
        None,
        123,
    ],
)
def test_authorization_operation_rejects_invalid_values(
    value,
):
    with pytest.raises(
        ValueError,
        match="Report authorization operation",
    ):
        ReportAuthorizationOperation.normalize(value)


def test_authorization_operation_exposes_code():
    assert (
        ReportAuthorizationOperation.EXECUTE.code
        == "execute"
    )


def test_authorization_operation_to_dict():
    assert (
        ReportAuthorizationOperation.EXPORT.to_dict()
        == {
            "code": "export",
        }
    )


# ---------------------------------------------------------
# Authorization Resource
# ---------------------------------------------------------


def test_authorization_resource_normalizes_type():
    resource = ReportAuthorizationResource(
        resource_type="  REPORT  ",
        identifier="sales.monthly",
    )

    assert resource.resource_type == "report"


def test_authorization_resource_requires_type():
    with pytest.raises(
        ValueError,
        match="resource_type",
    ):
        ReportAuthorizationResource(
            resource_type=" ",
            identifier="sales.monthly",
        )


@pytest.mark.parametrize(
    "identifier",
    [
        "",
        " ",
        None,
        123,
    ],
)
def test_authorization_resource_requires_identifier(
    identifier,
):
    with pytest.raises(
        ValueError,
        match="resource identifier",
    ):
        ReportAuthorizationResource(
            resource_type="report",
            identifier=identifier,
        )


def test_authorization_resource_canonical_identifier():
    resource = ReportAuthorizationResource(
        resource_type="report",
        identifier="sales.monthly",
    )

    assert (
        resource.canonical_identifier
        == "report:sales.monthly"
    )


def test_authorization_resource_copies_metadata():
    metadata = {
        "department": "finance",
    }

    resource = ReportAuthorizationResource(
        resource_type="report",
        identifier="sales.monthly",
        metadata=metadata,
    )

    metadata["department"] = "hr"

    assert (
        resource.metadata["department"]
        == "finance"
    )


def test_authorization_resource_rejects_non_dictionary_metadata():
    with pytest.raises(
        ValueError,
        match="resource metadata",
    ):
        ReportAuthorizationResource(
            resource_type="report",
            identifier="sales.monthly",
            metadata=[],
        )


def test_authorization_resource_to_dict():
    resource = ReportAuthorizationResource(
        resource_type="report",
        identifier="sales.monthly",
        metadata={
            "module": "reporting",
        },
    )

    result = resource.to_dict()

    assert result == {
        "resource_type": "report",
        "identifier": "sales.monthly",
        "canonical_identifier": (
            "report:sales.monthly"
        ),
        "metadata": {
            "module": "reporting",
        },
    }


# ---------------------------------------------------------
# Authorization Subject
# ---------------------------------------------------------


def test_authorization_subject_defaults_to_user():
    subject = ReportAuthorizationSubject(
        identifier="user-001",
    )

    assert subject.subject_type == "user"


def test_authorization_subject_normalizes_type():
    subject = ReportAuthorizationSubject(
        identifier="user-001",
        subject_type="  USER  ",
    )

    assert subject.subject_type == "user"


@pytest.mark.parametrize(
    "identifier",
    [
        "",
        " ",
        None,
        123,
    ],
)
def test_authorization_subject_requires_identifier(
    identifier,
):
    with pytest.raises(
        ValueError,
        match="subject identifier",
    ):
        ReportAuthorizationSubject(
            identifier=identifier,
        )


def test_authorization_subject_requires_type():
    with pytest.raises(
        ValueError,
        match="subject_type",
    ):
        ReportAuthorizationSubject(
            identifier="user-001",
            subject_type=" ",
        )


def test_authorization_subject_canonical_identifier():
    subject = ReportAuthorizationSubject(
        identifier="user-001",
        subject_type="user",
    )

    assert (
        subject.canonical_identifier
        == "user:user-001"
    )


def test_authorization_subject_to_dict():
    subject = ReportAuthorizationSubject(
        identifier="user-001",
        metadata={
            "source": "login",
        },
    )

    assert subject.to_dict() == {
        "identifier": "user-001",
        "subject_type": "user",
        "canonical_identifier": "user:user-001",
        "metadata": {
            "source": "login",
        },
    }


# ---------------------------------------------------------
# Authorization Context
# ---------------------------------------------------------


def test_authorization_context_defaults_to_empty_metadata():
    context = ReportAuthorizationContext()

    assert context.metadata == {}


def test_authorization_context_copies_metadata():
    metadata = {
        "organization": "SSRC",
    }

    context = ReportAuthorizationContext(
        metadata=metadata,
    )

    metadata["organization"] = "OTHER"

    assert (
        context.metadata["organization"]
        == "SSRC"
    )


def test_authorization_context_rejects_non_dictionary_metadata():
    with pytest.raises(
        ValueError,
        match="context metadata",
    ):
        ReportAuthorizationContext(
            metadata=[],
        )


def test_authorization_context_to_dict():
    context = ReportAuthorizationContext(
        metadata={
            "organization": "SSRC",
        },
    )

    assert context.to_dict() == {
        "metadata": {
            "organization": "SSRC",
        },
    }


# ---------------------------------------------------------
# Authorization Request
# ---------------------------------------------------------


def make_request():
    return ReportAuthorizationRequest(
        subject=ReportAuthorizationSubject(
            identifier="user-001",
        ),
        operation=ReportAuthorizationOperation.EXECUTE,
        resource=ReportAuthorizationResource(
            resource_type="report",
            identifier="sales.monthly",
        ),
        context=ReportAuthorizationContext(
            metadata={
                "module": "reporting",
            },
        ),
        metadata={
            "request_id": "REQ-001",
        },
    )


def test_authorization_request_constructs():
    request = make_request()

    assert request.subject.identifier == "user-001"

    assert (
        request.operation
        is ReportAuthorizationOperation.EXECUTE
    )

    assert (
        request.resource.identifier
        == "sales.monthly"
    )


def test_authorization_request_normalizes_string_operation():
    request = ReportAuthorizationRequest(
        subject=ReportAuthorizationSubject(
            identifier="user-001",
        ),
        operation="  EXECUTE  ",
        resource=ReportAuthorizationResource(
            resource_type="report",
            identifier="sales.monthly",
        ),
    )

    assert (
        request.operation
        is ReportAuthorizationOperation.EXECUTE
    )


@pytest.mark.parametrize(
    "field,value,pattern",
    [
        (
            "subject",
            "invalid",
            "request subject",
        ),
        (
            "operation",
            "invalid",
            "authorization operation",
        ),
        (
            "resource",
            "invalid",
            "request resource",
        ),
        (
            "context",
            "invalid",
            "request context",
        ),
    ],
)
def test_authorization_request_rejects_invalid_components(
    field,
    value,
    pattern,
):
    subject = ReportAuthorizationSubject(
        identifier="user-001",
    )

    resource = ReportAuthorizationResource(
        resource_type="report",
        identifier="sales.monthly",
    )

    values = {
        "subject": subject,
        "operation": ReportAuthorizationOperation.VIEW,
        "resource": resource,
        "context": ReportAuthorizationContext(),
    }

    values[field] = value

    with pytest.raises(
        ValueError,
        match=pattern,
    ):
        ReportAuthorizationRequest(
            **values
        )


def test_authorization_request_requires_metadata_dictionary():
    with pytest.raises(
        ValueError,
        match="request metadata",
    ):
        ReportAuthorizationRequest(
            subject=ReportAuthorizationSubject(
                identifier="user-001",
            ),
            operation=ReportAuthorizationOperation.VIEW,
            resource=ReportAuthorizationResource(
                resource_type="report",
                identifier="sales.monthly",
            ),
            metadata=[],
        )


def test_authorization_request_identifier_is_stable():
    request = make_request()

    assert (
        request.identifier
        == "user:user-001:"
        "execute:"
        "report:sales.monthly"
    )


def test_authorization_request_is_immutable():
    request = make_request()

    with pytest.raises(
        AttributeError,
    ):
        request.metadata = {}


def test_authorization_request_to_dict():
    request = make_request()

    result = request.to_dict()

    assert result["subject"]["identifier"] == "user-001"

    assert result["operation"] == {
        "code": "execute",
    }

    assert result["resource"]["identifier"] == (
        "sales.monthly"
    )

    assert result["context"] == {
        "metadata": {
            "module": "reporting",
        },
    }

    assert result["metadata"] == {
        "request_id": "REQ-001",
    }

    assert result["identifier"] == (
        "user:user-001:"
        "execute:"
        "report:sales.monthly"
    )


# ---------------------------------------------------------
# Authorization Decision Status
# ---------------------------------------------------------


@pytest.mark.parametrize(
    "value,expected",
    [
        (
            "allow",
            ReportAuthorizationDecisionStatus.ALLOW,
        ),
        (
            " ALLOW ",
            ReportAuthorizationDecisionStatus.ALLOW,
        ),
        (
            "deny",
            ReportAuthorizationDecisionStatus.DENY,
        ),
        (
            "DENY",
            ReportAuthorizationDecisionStatus.DENY,
        ),
    ],
)
def test_authorization_decision_status_normalizes_values(
    value,
    expected,
):
    assert (
        ReportAuthorizationDecisionStatus.normalize(value)
        is expected
    )


@pytest.mark.parametrize(
    "value",
    [
        "",
        " ",
        "unsupported",
        "pending",
        None,
        123,
    ],
)
def test_authorization_decision_status_rejects_invalid_values(
    value,
):
    with pytest.raises(
        ValueError,
        match="Report authorization decision status",
    ):
        ReportAuthorizationDecisionStatus.normalize(
            value
        )


def test_authorization_decision_status_exposes_state_helpers():
    assert (
        ReportAuthorizationDecisionStatus.ALLOW.is_allowed
        is True
    )

    assert (
        ReportAuthorizationDecisionStatus.ALLOW.is_denied
        is False
    )

    assert (
        ReportAuthorizationDecisionStatus.DENY.is_allowed
        is False
    )

    assert (
        ReportAuthorizationDecisionStatus.DENY.is_denied
        is True
    )


# ---------------------------------------------------------
# Authorization Decision
# ---------------------------------------------------------


def test_authorization_decision_accepts_string_status():
    decision = ReportAuthorizationDecision(
        status="allow",
        reason="Permission granted.",
    )

    assert (
        decision.status
        is ReportAuthorizationDecisionStatus.ALLOW
    )


def test_authorization_decision_allows_request():
    decision = ReportAuthorizationDecision(
        status=ReportAuthorizationDecisionStatus.ALLOW,
        reason="Permission granted.",
    )

    assert decision.is_allowed is True
    assert decision.is_denied is False


def test_authorization_decision_denies_request():
    decision = ReportAuthorizationDecision(
        status=ReportAuthorizationDecisionStatus.DENY,
        reason="Permission denied.",
    )

    assert decision.is_allowed is False
    assert decision.is_denied is True


def test_authorization_decision_normalizes_reason():
    decision = ReportAuthorizationDecision(
        status="deny",
        reason="  Permission denied.  ",
    )

    assert decision.reason == "Permission denied."


def test_authorization_decision_normalizes_blank_reason():
    decision = ReportAuthorizationDecision(
        status="deny",
        reason=" ",
    )

    assert decision.reason is None


@pytest.mark.parametrize(
    "reason",
    [
        123,
        [],
        {},
    ],
)
def test_authorization_decision_rejects_invalid_reason(
    reason,
):
    with pytest.raises(
        ValueError,
        match="decision reason",
    ):
        ReportAuthorizationDecision(
            status="deny",
            reason=reason,
        )


def test_authorization_decision_rejects_invalid_status():
    with pytest.raises(
        ValueError,
        match="Report authorization decision status",
    ):
        ReportAuthorizationDecision(
            status="unsupported",
        )


def test_authorization_decision_rejects_invalid_metadata():
    with pytest.raises(
        ValueError,
        match="decision metadata",
    ):
        ReportAuthorizationDecision(
            status="deny",
            metadata=[],
        )


def test_authorization_decision_copies_metadata():
    metadata = {
        "policy": "report.execute",
    }

    decision = ReportAuthorizationDecision(
        status="allow",
        metadata=metadata,
    )

    metadata["policy"] = "changed"

    assert (
        decision.metadata["policy"]
        == "report.execute"
    )


def test_authorization_decision_is_immutable():
    decision = ReportAuthorizationDecision(
        status="allow",
    )

    with pytest.raises(
        AttributeError,
    ):
        decision.reason = "changed"


def test_authorization_decision_to_dict():
    decision = ReportAuthorizationDecision(
        status="allow",
        reason="Permission granted.",
        metadata={
            "policy": "report.execute",
        },
    )

    assert decision.to_dict() == {
        "status": "allow",
        "reason": "Permission granted.",
        "metadata": {
            "policy": "report.execute",
        },
        "is_allowed": True,
        "is_denied": False,
    }
