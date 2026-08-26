"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting & Analytics Framework Tests

Reporting audit integration boundary tests.
"""

from __future__ import annotations

import pytest

from app.core.reporting.audit import (
    ReportAuditEvent,
    ReportingAuditAdapter,
    ReportingGovernanceAdapter,
)
from app.core.security.audit import (
    SecurityAuditEvent,
)
from app.core.security.audit_registry import (
    AuditRegistry,
)


def make_event(
    event_type: str = "REPORT_EXECUTED",
) -> ReportAuditEvent:
    """
    Create a minimal reporting audit event.
    """

    return ReportAuditEvent(
        event_type=event_type,
        subject="user-001",
        resource="report:TEST-REPORT",
        action="EXECUTE",
        result="SUCCESS",
        message="Report executed successfully.",
        metadata={
            "source": "unit-test",
            "request_id": "REQ-001",
        },
    )


def test_report_audit_event_accepts_valid_event():

    event = make_event()

    assert (
        event.event_type
        == "REPORT_EXECUTED"
    )

    assert (
        event.subject
        == "user-001"
    )

    assert (
        event.resource
        == "report:TEST-REPORT"
    )

    assert (
        event.action
        == "EXECUTE"
    )

    assert (
        event.result
        == "SUCCESS"
    )


def test_report_audit_event_rejects_missing_event_type():

    with pytest.raises(
        ValueError,
        match="Reporting audit event type is required",
    ):
        ReportAuditEvent(
            event_type=""
        )


def test_report_audit_event_rejects_invalid_metadata():

    with pytest.raises(
        ValueError,
        match="metadata must be a dictionary",
    ):
        ReportAuditEvent(
            event_type="REPORT_EXECUTED",
            metadata=[],
        )


def test_reporting_audit_adapter_requires_audit_registry():

    with pytest.raises(
        ValueError,
        match="AuditRegistry",
    ):
        ReportingAuditAdapter(
            object()
        )


def test_reporting_audit_adapter_accepts_audit_registry():

    registry = AuditRegistry()

    adapter = ReportingAuditAdapter(
        registry
    )

    assert (
        adapter.audit_registry
        is registry
    )


def test_reporting_audit_adapter_rejects_invalid_event():

    adapter = ReportingAuditAdapter(
        AuditRegistry()
    )

    with pytest.raises(
        ValueError,
        match="ReportAuditEvent",
    ):
        adapter.record(
            object()
        )


def test_reporting_audit_adapter_translates_event():

    registry = AuditRegistry()

    adapter = ReportingAuditAdapter(
        registry
    )

    event = make_event()

    recorded = adapter.record(
        event
    )

    assert isinstance(
        recorded,
        SecurityAuditEvent,
    )

    assert (
        recorded.event_type
        == event.event_type
    )

    assert (
        recorded.subject
        == event.subject
    )

    assert (
        recorded.resource
        == event.resource
    )

    assert (
        recorded.action
        == event.action
    )

    assert (
        recorded.result
        == event.result
    )

    assert (
        recorded.message
        == event.message
    )


def test_reporting_audit_adapter_preserves_metadata():

    registry = AuditRegistry()

    adapter = ReportingAuditAdapter(
        registry
    )

    event = make_event()

    recorded = adapter.record(
        event
    )

    assert (
        recorded.metadata
        == event.metadata
    )

    assert (
        recorded.metadata
        is not event.metadata
    )


def test_reporting_audit_adapter_records_event():

    registry = AuditRegistry()

    adapter = ReportingAuditAdapter(
        registry
    )

    event = make_event()

    recorded = adapter.record(
        event
    )

    events = registry.all()

    assert len(events) == 1

    assert (
        events[0]
        is recorded
    )


def test_reporting_audit_adapter_returns_recorded_event():

    registry = AuditRegistry()

    adapter = ReportingAuditAdapter(
        registry
    )

    recorded = adapter.record(
        make_event()
    )

    assert (
        recorded
        is registry.all()[0]
    )


def test_reporting_audit_adapter_preserves_multiple_events():

    registry = AuditRegistry()

    adapter = ReportingAuditAdapter(
        registry
    )

    first = adapter.record(
        make_event(
            "REPORT_EXECUTED"
        )
    )

    second = adapter.record(
        make_event(
            "REPORT_EXPORTED"
        )
    )

    events = registry.all()

    assert len(events) == 2

    assert events[0] is first
    assert events[1] is second

    assert (
        events[0].event_type
        == "REPORT_EXECUTED"
    )

    assert (
        events[1].event_type
        == "REPORT_EXPORTED"
    )


def test_reporting_audit_adapter_does_not_modify_event_metadata():

    metadata = {
        "source": "unit-test",
        "request_id": "REQ-002",
    }

    event = ReportAuditEvent(
        event_type="REPORT_EXECUTED",
        metadata=metadata,
    )

    original = dict(
        metadata
    )

    adapter = ReportingAuditAdapter(
        AuditRegistry()
    )

    adapter.record(
        event
    )

    assert (
        metadata
        == original
    )

    assert (
        event.metadata
        == original
    )


def test_reporting_audit_adapter_supports_failure_events():

    registry = AuditRegistry()

    adapter = ReportingAuditAdapter(
        registry
    )

    event = ReportAuditEvent(
        event_type="REPORT_EXECUTION_FAILED",
        subject="user-001",
        resource="report:TEST-REPORT",
        action="EXECUTE",
        result="FAILURE",
        message="Report execution failed.",
        metadata={
            "error_code": "REPORT-001",
        },
    )

    recorded = adapter.record(
        event
    )

    assert (
        recorded.result
        == "FAILURE"
    )

    assert (
        recorded.message
        == "Report execution failed."
    )

    assert (
        recorded.metadata["error_code"]
        == "REPORT-001"
    )

def test_reporting_governance_adapter_requires_report_audit_event():
    adapter = ReportingGovernanceAdapter()

    with pytest.raises(
        ValueError,
        match="ReportAuditEvent",
    ):
        adapter.enrich(
            "invalid-event",
        )


def test_reporting_governance_adapter_adds_governance_metadata():
    adapter = ReportingGovernanceAdapter()

    event = make_event()

    result = adapter.enrich(
        event,
        governance_state="COMPLETED",
        governance_decision="ALLOW",
        governance_reason="Authorized reporting activity.",
    )

    assert result is event
    assert event.metadata["governance_state"] == "COMPLETED"
    assert event.metadata["governance_decision"] == "ALLOW"
    assert (
        event.metadata["governance_reason"]
        == "Authorized reporting activity."
    )


def test_reporting_governance_adapter_preserves_existing_metadata():
    adapter = ReportingGovernanceAdapter()

    event = make_event()

    event.metadata.update(
        {
        "correlation_id": "corr-001",
        "source": "reporting",
        }
    )

    adapter.enrich(
        event,
        governance_state="STARTED",
    )

    assert event.metadata["correlation_id"] == "corr-001"
    assert event.metadata["source"] == "reporting"
    assert event.metadata["governance_state"] == "STARTED"


def test_reporting_governance_adapter_does_not_add_missing_governance_values():
    adapter = ReportingGovernanceAdapter()

    event = make_event()

    adapter.enrich(event)

    assert "governance_state" not in event.metadata
    assert "governance_decision" not in event.metadata
    assert "governance_reason" not in event.metadata


__all__ = []
