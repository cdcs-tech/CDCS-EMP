"""
CDCS Enterprise Management Platform (CDCS-EMP)

Sprint 1.15.6

Focused tests for authorization scope integration.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.core.execution.context import (
    ExecutionContext,
)

from app.core.security.authorization_scope import (
    AuthorizationScope,
    AuthorizationScopeException,
    AuthorizationScopeMismatchException,
    AuthorizationScopeResolutionException,
    AuthorizationScopeService,
    ScopedAuthorizationDecision,
)

from app.core.platform.scope import (
    UserScope,
)


@dataclass
class FakeUser:
    """
    Minimal user double for scope-resolution tests.
    """

    user_id: str = "user-001"
    username: str = "scope.user"


class FakeScopeResolver:
    """
    Minimal scope-resolver double.
    """

    resolved_scope = UserScope(
        user_id="user-001",
        username="scope.user",
        tenant_id="tenant-001",
        organization_id="org-001",
    )

    @classmethod
    def resolve(cls, user):
        return cls.resolved_scope


class MissingScopeResolver:
    """
    Scope resolver that simulates missing scope.
    """

    @staticmethod
    def resolve(user):
        return None


class FailingScopeResolver:
    """
    Scope resolver that simulates a platform scope failure.
    """

    @staticmethod
    def resolve(user):
        from app.core.platform.scope import (
            PlatformScopeResolutionException,
        )

        raise PlatformScopeResolutionException(
            "Scope resolution failed."
        )


class FakeAuthorizationEngine:
    """
    Minimal AuthorizationEngine-compatible test double.
    """

    def __init__(
        self,
        allowed: bool = True,
    ) -> None:
        self.allowed = allowed
        self.calls: list[dict] = []

    def can(
        self,
        subject,
        permission_code: str,
        policies=None,
        context=None,
    ) -> bool:
        self.calls.append(
            {
                "subject": subject,
                "permission_code": permission_code,
                "policies": policies,
                "context": context,
            }
        )

        return self.allowed


def build_service(
    *,
    allowed: bool = True,
    resolver=FakeScopeResolver,
):
    """
    Build an authorization scope service with test doubles.
    """

    engine = FakeAuthorizationEngine(
        allowed=allowed
    )

    service = AuthorizationScopeService(
        authorization_engine=engine,
        scope_resolver=resolver,
    )

    return service, engine


def test_authorization_scope_service_resolves_active_scope():
    """
    Active user scope should be resolved into AuthorizationScope.
    """

    service, _ = build_service()

    scope = service.resolve_scope(
        FakeUser()
    )

    assert isinstance(
        scope,
        AuthorizationScope,
    )

    assert scope.user_id == "user-001"
    assert scope.username == "scope.user"
    assert scope.tenant_id == "tenant-001"
    assert scope.organization_id == "org-001"


def test_authorization_scope_service_rejects_missing_scope():
    """
    Authorization must fail when no active scope exists.
    """

    service, _ = build_service(
        resolver=MissingScopeResolver
    )

    with pytest.raises(
        AuthorizationScopeResolutionException
    ):
        service.resolve_scope(
            FakeUser()
        )


def test_authorization_scope_service_translates_platform_scope_failure():
    """
    Platform scope-resolution failures should be translated
    into authorization scope failures.
    """

    service, _ = build_service(
        resolver=FailingScopeResolver
    )

    with pytest.raises(
        AuthorizationScopeResolutionException,
        match="Scope resolution failed",
    ):
        service.resolve_scope(
            FakeUser()
        )


def test_matching_explicit_scope_is_accepted():
    """
    Explicit tenant and organization scope matching the
    active scope should be accepted.
    """

    service, _ = build_service()

    scope = service.resolve_scope(
        FakeUser()
    )

    service.validate_scope(
        scope,
        tenant_id="tenant-001",
        organization_id="org-001",
    )


def test_mismatched_tenant_scope_is_rejected():
    """
    An explicitly requested tenant outside the active scope
    must be rejected.
    """

    service, _ = build_service()

    scope = service.resolve_scope(
        FakeUser()
    )

    with pytest.raises(
        AuthorizationScopeMismatchException
    ):
        service.validate_scope(
            scope,
            tenant_id="tenant-999",
        )


def test_mismatched_organization_scope_is_rejected():
    """
    An explicitly requested organization outside the active
    scope must be rejected.
    """

    service, _ = build_service()

    scope = service.resolve_scope(
        FakeUser()
    )

    with pytest.raises(
        AuthorizationScopeMismatchException
    ):
        service.validate_scope(
            scope,
            organization_id="org-999",
        )


def test_authorize_delegates_to_authorization_engine():
    """
    RBAC authorization should be delegated to the existing
    AuthorizationEngine boundary.
    """

    service, engine = build_service()

    decision = service.authorize(
        FakeUser(),
        "test.permission",
    )

    assert len(
        engine.calls
    ) == 1

    call = engine.calls[0]

    assert call["subject"] == "user-001"
    assert (
        call["permission_code"]
        == "test.permission"
    )


def test_authorize_passes_scope_into_context():
    """
    Scope information should be supplied to the authorization
    engine through the authorization context.
    """

    service, engine = build_service()

    service.authorize(
        FakeUser(),
        "test.permission",
    )

    context = engine.calls[0]["context"]

    assert context["user_id"] == "user-001"
    assert context["tenant_id"] == "tenant-001"
    assert context["organization_id"] == "org-001"


def test_authorize_enriches_execution_context_without_mutation():
    """
    An ExecutionContext should be enriched without mutating
    the original context.
    """

    service, engine = build_service()

    context = ExecutionContext(
        user_id="user-001",
        module_name="test",
        operation="authorize",
        metadata={
            "source": "unit-test",
        },
    )

    decision = service.authorize(
        FakeUser(),
        "test.permission",
        context=context,
    )

    enriched = engine.calls[0]["context"]

    assert enriched is not context

    assert (
        context.metadata
        == {
            "source": "unit-test",
        }
    )

    assert enriched.metadata["source"] == "unit-test"
    assert enriched.metadata["user_id"] == "user-001"
    assert enriched.metadata["tenant_id"] == "tenant-001"
    assert (
        enriched.metadata["organization_id"]
        == "org-001"
    )


def test_authorize_enriches_dictionary_context():
    """
    Dictionary authorization contexts should receive scope
    metadata without mutating the original dictionary.
    """

    service, engine = build_service()

    context = {
        "source": "unit-test",
    }

    service.authorize(
        FakeUser(),
        "test.permission",
        context=context,
    )

    enriched = engine.calls[0]["context"]

    assert enriched is not context

    assert context == {
        "source": "unit-test",
    }

    assert enriched["source"] == "unit-test"
    assert enriched["user_id"] == "user-001"
    assert enriched["tenant_id"] == "tenant-001"
    assert enriched["organization_id"] == "org-001"


def test_authorize_returns_allowed_scoped_decision():
    """
    Successful authorization should return an allowed
    ScopedAuthorizationDecision.
    """

    service, _ = build_service(
        allowed=True
    )

    decision = service.authorize(
        FakeUser(),
        "test.permission",
    )

    assert isinstance(
        decision,
        ScopedAuthorizationDecision,
    )

    assert decision.is_allowed()
    assert not decision.is_denied()

    assert (
        decision.permission_code
        == "test.permission"
    )

    assert decision.scope.tenant_id == "tenant-001"
    assert (
        decision.scope.organization_id
        == "org-001"
    )


def test_authorize_returns_denied_scoped_decision():
    """
    Failed RBAC authorization should return a denied
    ScopedAuthorizationDecision.
    """

    service, _ = build_service(
        allowed=False
    )

    decision = service.authorize(
        FakeUser(),
        "test.permission",
    )

    assert isinstance(
        decision,
        ScopedAuthorizationDecision,
    )

    assert decision.is_denied()
    assert not decision.is_allowed()


def test_authorize_rejects_mismatched_requested_scope():
    """
    Authorization must not proceed when the requested scope
    differs from the user's active scope.
    """

    service, engine = build_service()

    with pytest.raises(
        AuthorizationScopeMismatchException
    ):
        service.authorize(
            FakeUser(),
            "test.permission",
            tenant_id="tenant-999",
        )

    assert len(
        engine.calls
    ) == 0


def test_authorize_rejects_missing_permission_code():
    """
    A permission code is mandatory for scoped authorization.
    """

    service, _ = build_service()

    with pytest.raises(
        AuthorizationScopeException,
        match="Permission code is required",
    ):
        service.authorize(
            FakeUser(),
            "",
        )


def test_authorization_scope_serializes_context():
    """
    AuthorizationScope should expose a serialization-friendly
    representation.
    """

    scope = AuthorizationScope(
        user_id="user-001",
        username="scope.user",
        tenant_id="tenant-001",
        organization_id="org-001",
    )

    assert scope.as_context() == {
        "user_id": "user-001",
        "tenant_id": "tenant-001",
        "organization_id": "org-001",
        "username": "scope.user",
    }
