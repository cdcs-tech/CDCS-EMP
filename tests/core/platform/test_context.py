"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure Tests

Request context tests.
"""

from app.core.platform import (
    PlatformConfig,
    RequestContext,
    RuntimeContext,
)


def create_runtime():

    config = PlatformConfig(
        environment="testing",
        debug=False,
        testing=True,
        app_name="CDCS-EMP",
        app_version="1.0.0",
    )

    return RuntimeContext(
        config=config
    )


def test_request_context_creation():

    runtime = create_runtime()

    context = RequestContext(
        runtime=runtime,
        user_id="user-001",
        username="admin",
        module_name="finance",
        operation="create",
        resource="invoice",
        source="web",
    )

    assert context.request_id

    assert (
        context.user_id
        == "user-001"
    )

    assert (
        context.username
        == "admin"
    )

    assert (
        context.module_name
        == "finance"
    )

    assert (
        context.operation
        == "create"
    )

    assert (
        context.resource
        == "invoice"
    )

    assert (
        context.source
        == "web"
    )


def test_request_context_runtime_information():

    runtime = create_runtime()

    context = RequestContext(
        runtime=runtime
    )

    assert (
        context.environment
        == "testing"
    )

    assert (
        context.application_name
        == "CDCS-EMP"
    )

    assert (
        context.application_version
        == "1.0.0"
    )


def test_request_identity():

    runtime = create_runtime()

    context = RequestContext(
        runtime=runtime,
        user_id="user-002",
        username="operator",
        module_name="hr",
        operation="update",
        resource="employee",
    )

    identity = context.identity()

    assert (
        identity["request_id"]
        == context.request_id
    )

    assert (
        identity["user_id"]
        == "user-002"
    )

    assert (
        identity["username"]
        == "operator"
    )

    assert (
        identity["module_name"]
        == "hr"
    )

    assert (
        identity["operation"]
        == "update"
    )

    assert (
        identity["resource"]
        == "employee"
    )


def test_runtime_identity():

    runtime = create_runtime()

    context = RequestContext(
        runtime=runtime
    )

    identity = context.runtime_identity()

    assert (
        identity["application_name"]
        == "CDCS-EMP"
    )

    assert (
        identity["application_version"]
        == "1.0.0"
    )

    assert (
        identity["environment"]
        == "testing"
    )


def test_context_as_dict():

    runtime = create_runtime()

    context = RequestContext(
        runtime=runtime,
        user_id="user-003",
        module_name="procurement",
        operation="approve",
    )

    data = context.as_dict()

    assert (
        data["request_id"]
        == context.request_id
    )

    assert (
        data["user_id"]
        == "user-003"
    )

    assert (
        data["module_name"]
        == "procurement"
    )

    assert (
        data["operation"]
        == "approve"
    )

    assert (
        data["environment"]
        == "testing"
    )

    assert (
        data["application_name"]
        == "CDCS-EMP"
    )

    assert (
        "created_at"
        in data
    )


def test_metadata_management():

    runtime = create_runtime()

    context = RequestContext(
        runtime=runtime
    )

    context.add_metadata(
        "ip_address",
        "127.0.0.1",
    )

    context.add_metadata(
        "channel",
        "web",
    )

    assert (
        context.metadata["ip_address"]
        == "127.0.0.1"
    )

    assert (
        context.metadata["channel"]
        == "web"
    )


def test_context_validation():

    runtime = create_runtime()

    context = RequestContext(
        runtime=runtime
    )

    assert (
        context.validate()
        is True
    )


def test_context_representation():

    runtime = create_runtime()

    context = RequestContext(
        runtime=runtime,
        module_name="finance",
        operation="create",
    )

    representation = repr(
        context
    )

    assert (
        "RequestContext"
        in representation
    )

    assert (
        "request_id="
        in representation
    )

    assert (
        "module="
        in representation
    )

    assert (
        "operation="
        in representation
    )

def test_request_context_supports_tenant_and_organization():

    runtime = create_runtime()

    context = RequestContext(
        runtime=runtime,
        user_id="user-001",
        tenant_id="tenant-001",
        organization_id="org-001",
        module_name="finance",
        operation="create",
    )

    assert (
        context.tenant_id
        == "tenant-001"
    )

    assert (
        context.organization_id
        == "org-001"
    )

def test_request_identity_contains_tenant_and_organization():

    runtime = create_runtime()

    context = RequestContext(
        runtime=runtime,
        user_id="user-001",
        tenant_id="tenant-001",
        organization_id="org-001",
        module_name="finance",
        operation="create",
    )

    identity = context.identity()

    assert (
        identity["tenant_id"]
        == "tenant-001"
    )

    assert (
        identity["organization_id"]
        == "org-001"
    )

def test_child_context_preserves_tenant_and_organization():

    runtime = create_runtime()

    context = RequestContext(
        runtime=runtime,
        user_id="user-001",
        tenant_id="tenant-001",
        organization_id="org-001",
        module_name="finance",
        operation="create",
    )

    child = context.child_context()

    assert (
        child.tenant_id
        == "tenant-001"
    )

    assert (
        child.organization_id
        == "org-001"
    )

    assert (
        child.correlation_id
        == context.correlation_id
    )

