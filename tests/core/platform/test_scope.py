"""
CDCS Enterprise Management Platform (CDCS-EMP)

Platform Infrastructure Tests

User Scope Resolution.
"""
from unittest.mock import Mock
from types import SimpleNamespace

import pytest

from app.core.platform import (
    PlatformScopeAmbiguityException,
    PlatformScopeResolutionException,
    UserScope,
    UserScopeResolver,
)
from app.extensions import db
from app.models import (
    Organization,
    OrganizationMembership,
    Tenant,
    User,
)

@pytest.fixture(autouse=True)
def application_context(app):
    """
    Ensure all scope resolution tests execute
    within the Flask application context.
    """

    yield


def create_user(
    username="scope-user",
    active=True,
    deleted=False,
):
    user = User(
        username=username,
        email=f"{username}@example.com",
        password_hash="test-password",
        first_name="Scope",
        last_name="User",
        is_active=active,
        is_deleted=deleted,
    )

    db.session.add(user)
    db.session.flush()

    return user


def create_tenant(
    code="TENANT-001",
    active=True,
):
    tenant = Tenant(
        code=code,
        name="Test Tenant",
        is_active=active,
    )

    db.session.add(tenant)
    db.session.flush()

    return tenant


def create_organization(
    tenant,
    code="ORG-001",
    active=True,
):
    organization = Organization(
        tenant_id=tenant.id,
        code=code,
        name="Test Organization",
        is_active=active,
    )

    db.session.add(organization)
    db.session.flush()

    return organization


def create_membership(
    user,
    organization,
    active=True,
):
    membership = OrganizationMembership(
        user_id=user.id,
        organization_id=organization.id,
        is_active=active,
    )

    db.session.add(membership)
    db.session.flush()

    return membership


def test_resolve_returns_none_for_missing_user():

    scope = UserScopeResolver.resolve(
        None
    )

    assert scope is None


def test_resolve_valid_single_active_membership():

    user = create_user()

    tenant = create_tenant()

    organization = create_organization(
        tenant
    )

    create_membership(
        user,
        organization,
    )

    scope = UserScopeResolver.resolve(
        user
    )

    assert isinstance(
        scope,
        UserScope,
    )

    assert (
        scope.user_id
        == str(user.id)
    )

    assert (
        scope.username
        == user.username
    )

    assert (
        scope.tenant_id
        == str(tenant.id)
    )

    assert (
        scope.organization_id
        == str(organization.id)
    )


def test_resolve_rejects_inactive_user():

    user = create_user(
        active=False
    )

    with pytest.raises(
        PlatformScopeResolutionException,
        match="User is inactive",
    ):

        UserScopeResolver.resolve(
            user
        )


def test_resolve_rejects_deleted_user():

    user = create_user(
        deleted=True
    )

    with pytest.raises(
        PlatformScopeResolutionException,
        match="User is deleted",
    ):

        UserScopeResolver.resolve(
            user
        )


def test_resolve_rejects_missing_active_membership():

    user = create_user()

    with pytest.raises(
        PlatformScopeResolutionException,
        match="no active organization membership",
    ):

        UserScopeResolver.resolve(
            user
        )


def test_resolve_ignores_inactive_membership():

    user = create_user()

    tenant = create_tenant()

    organization = create_organization(
        tenant
    )

    create_membership(
        user,
        organization,
        active=False,
    )

    with pytest.raises(
        PlatformScopeResolutionException,
        match="no active organization membership",
    ):

        UserScopeResolver.resolve(
            user
        )


def test_resolve_rejects_multiple_active_memberships():

    user = create_user()

    tenant_one = create_tenant(
        code="TENANT-001"
    )

    tenant_two = create_tenant(
        code="TENANT-002"
    )

    organization_one = create_organization(
        tenant_one,
        code="ORG-001",
    )

    organization_two = create_organization(
        tenant_two,
        code="ORG-002",
    )

    create_membership(
        user,
        organization_one,
    )

    create_membership(
        user,
        organization_two,
    )

    with pytest.raises(
        PlatformScopeAmbiguityException,
        match="multiple active organization memberships",
    ):

        UserScopeResolver.resolve(
            user
        )


def test_resolve_rejects_missing_organization():

    organization_membership = SimpleNamespace(
        is_active=True,
        organization=None,
    )

    user = SimpleNamespace(
        id=1,
        username="scope-user",
        is_active=True,
        is_deleted=False,
        organization_memberships=[
            organization_membership
        ],
    )

    with pytest.raises(
        PlatformScopeResolutionException,
        match="no associated organization",
    ):

        UserScopeResolver.resolve(
            user
        )


def test_resolve_rejects_inactive_organization():

    user = create_user()

    tenant = create_tenant()

    organization = create_organization(
        tenant,
        active=False,
    )

    create_membership(
        user,
        organization,
    )

    with pytest.raises(
        PlatformScopeResolutionException,
        match="Organization is inactive",
    ):

        UserScopeResolver.resolve(
            user
        )


def test_resolve_rejects_missing_tenant():

    organization = SimpleNamespace(
        id=1,
        is_active=True,
        tenant=None,
    )

    organization_membership = SimpleNamespace(
        is_active=True,
        organization=organization,
    )

    user = SimpleNamespace(
        id=1,
        username="scope-user",
        is_active=True,
        is_deleted=False,
        organization_memberships=[
            organization_membership
        ],
    )

    with pytest.raises(
        PlatformScopeResolutionException,
        match="no associated tenant",
    ):

        UserScopeResolver.resolve(
            user
        )


def test_resolve_rejects_inactive_tenant():

    user = create_user()

    tenant = create_tenant(
        active=False
    )

    organization = create_organization(
        tenant
    )

    create_membership(
        user,
        organization,
    )

    with pytest.raises(
        PlatformScopeResolutionException,
        match="Tenant is inactive",
    ):

        UserScopeResolver.resolve(
            user
        )


def test_resolve_rejects_missing_user_id():

    user = Mock()

    user.is_active = True
    user.is_deleted = False
    user.id = None
    user.username = "scope-user"

    tenant = Mock()
    tenant.is_active = True
    tenant.id = 1

    organization = Mock()
    organization.is_active = True
    organization.id = 1
    organization.tenant = tenant

    membership = Mock()
    membership.is_active = True
    membership.organization = organization

    user.organization_memberships = [
        membership
    ]

    with pytest.raises(
        PlatformScopeResolutionException,
        match="User ID is required",
    ):

        UserScopeResolver.resolve(
            user
        )


def test_resolve_authenticated_returns_none_for_anonymous_user(
    app,
):

    with app.test_request_context():

        scope = (
            UserScopeResolver
            .resolve_authenticated()
        )

        assert scope is None
