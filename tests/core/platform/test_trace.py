"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure Tests

Correlation and trace context tests.
"""

from app.core.platform import (
    TraceContext,
    generate_id,
)


def test_generate_id():

    identifier = generate_id(
        "TEST"
    )

    assert identifier.startswith(
        "TEST-"
    )

    assert len(identifier) > 5


def test_trace_context_creation():

    trace = TraceContext()

    assert trace.correlation_id
    assert trace.trace_id
    assert trace.span_id

    assert (
        trace.parent_trace_id
        is None
    )


def test_trace_context_identity():

    trace = TraceContext()

    identity = trace.identity()

    assert (
        identity["correlation_id"]
        == trace.correlation_id
    )

    assert (
        identity["trace_id"]
        == trace.trace_id
    )

    assert (
        identity["parent_trace_id"]
        is None
    )

    assert (
        identity["span_id"]
        == trace.span_id
    )


def test_child_trace():

    parent = TraceContext()

    child = parent.child()

    assert (
        child.correlation_id
        == parent.correlation_id
    )

    assert (
        child.trace_id
        != parent.trace_id
    )

    assert (
        child.parent_trace_id
        == parent.trace_id
    )

    assert (
        child.span_id
        != parent.span_id
    )


def test_trace_validation():

    trace = TraceContext()

    assert (
        trace.validate()
        is True
    )


def test_trace_representation():

    trace = TraceContext()

    representation = repr(
        trace
    )

    assert (
        "TraceContext"
        in representation
    )

    assert (
        "correlation_id="
        in representation
    )

    assert (
        "trace_id="
        in representation
    )


def test_request_context_contains_trace():

    from app.core.platform import (
        PlatformConfig,
        RequestContext,
        RuntimeContext,
    )

    runtime = RuntimeContext(
        config=PlatformConfig(
            environment="testing",
            testing=True,
        )
    )

    context = RequestContext(
        runtime=runtime
    )

    assert context.trace

    assert (
        context.trace.correlation_id
    )

    assert (
        context.trace.trace_id
    )


def test_request_context_exposes_trace_identity():

    from app.core.platform import (
        PlatformConfig,
        RequestContext,
        RuntimeContext,
    )

    runtime = RuntimeContext(
        config=PlatformConfig(
            environment="testing",
            testing=True,
        )
    )

    context = RequestContext(
        runtime=runtime
    )

    identity = context.identity()

    assert (
        identity["correlation_id"]
        == context.trace.correlation_id
    )

    assert (
        identity["trace_id"]
        == context.trace.trace_id
    )


def test_request_context_as_dict_contains_trace():

    from app.core.platform import (
        PlatformConfig,
        RequestContext,
        RuntimeContext,
    )

    runtime = RuntimeContext(
        config=PlatformConfig(
            environment="testing",
            testing=True,
        )
    )

    context = RequestContext(
        runtime=runtime
    )

    data = context.as_dict()

    assert (
        data["correlation_id"]
        == context.trace.correlation_id
    )

    assert (
        data["trace_id"]
        == context.trace.trace_id
    )
