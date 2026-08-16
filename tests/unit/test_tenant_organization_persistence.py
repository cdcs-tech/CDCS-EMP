"""
CDCS Enterprise Management Platform (CDCS-EMP)

Stage 1.15.3
Tenant & Organization Persistence and Relationship Integrity Tests
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.organization import Organization
from app.models.organization_membership import (
    OrganizationMembership,
)
from app.models.tenant import Tenant
from app.models.user import User


# ------------------------------------------------------------------
# Tenant Persistence
# ------------------------------------------------------------------


def test_tenant_can_be_persisted(session):
    """
    Verify that a tenant can be persisted and retrieved.
    """

    tenant = Tenant(
        code="TENANT001",
        name="Test Tenant",
    )

    session.add(tenant)
    session.commit()

    persisted = session.get(Tenant, tenant.id)

    assert persisted is not None
    assert persisted.code == "TENANT001"
    assert persisted.name == "Test Tenant"
    assert persisted.is_active is True


def test_tenant_code_must_be_unique(session):
    """
    Verify that tenant codes are globally unique.
    """

    first = Tenant(
        code="TENANT001",
        name="First Tenant",
    )

    second = Tenant(
        code="TENANT001",
        name="Second Tenant",
    )

    session.add(first)
    session.commit()

    session.add(second)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()


# ------------------------------------------------------------------
# Organization Persistence
# ------------------------------------------------------------------


def test_organization_can_be_persisted_for_tenant(session):
    """
    Verify that an organization can be persisted under
    a tenant and retrieved with its tenant relationship.
    """

    tenant = Tenant(
        code="TENANT001",
        name="Test Tenant",
    )

    organization = Organization(
        code="ORG001",
        name="Test Organization",
        tenant=tenant,
    )

    session.add(organization)
    session.commit()

    persisted = session.get(
        Organization,
        organization.id,
    )

    assert persisted is not None
    assert persisted.tenant_id == tenant.id
    assert persisted.code == "ORG001"
    assert persisted.name == "Test Organization"
    assert persisted.is_active is True

    assert persisted.tenant is tenant


def test_tenant_organizations_relationship(session):
    """
    Verify the Tenant -> Organizations relationship.
    """

    tenant = Tenant(
        code="TENANT001",
        name="Test Tenant",
    )

    organization_one = Organization(
        code="ORG001",
        name="Organization One",
        tenant=tenant,
    )

    organization_two = Organization(
        code="ORG002",
        name="Organization Two",
        tenant=tenant,
    )

    session.add(tenant)
    session.commit()

    assert len(tenant.organizations) == 2
    assert organization_one in tenant.organizations
    assert organization_two in tenant.organizations


def test_organization_code_is_unique_within_tenant(session):
    """
    Verify that an organization code must be unique within
    a tenant.
    """

    tenant = Tenant(
        code="TENANT001",
        name="Test Tenant",
    )

    first = Organization(
        code="ORG001",
        name="First Organization",
        tenant=tenant,
    )

    session.add(first)
    session.commit()

    second = Organization(
        code="ORG001",
        name="Second Organization",
        tenant=tenant,
    )

    session.add(second)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()


def test_same_organization_code_is_allowed_across_tenants(
    session,
):
    """
    Verify that the same organization code can exist in
    different tenants.
    """

    tenant_one = Tenant(
        code="TENANT001",
        name="Tenant One",
    )

    tenant_two = Tenant(
        code="TENANT002",
        name="Tenant Two",
    )

    organization_one = Organization(
        code="ORG001",
        name="Organization One",
        tenant=tenant_one,
    )

    organization_two = Organization(
        code="ORG001",
        name="Organization Two",
        tenant=tenant_two,
    )

    session.add_all(
        [
            tenant_one,
            tenant_two,
            organization_one,
            organization_two,
        ]
    )

    session.commit()

    assert organization_one.id != organization_two.id
    assert organization_one.tenant_id != organization_two.tenant_id
    assert organization_one.code == organization_two.code


# ------------------------------------------------------------------
# Organization Membership Persistence
# ------------------------------------------------------------------


def test_membership_can_be_persisted(
    session,
):
    """
    Verify that a user can be associated with an organization.
    """

    tenant = Tenant(
        code="TENANT001",
        name="Test Tenant",
    )

    organization = Organization(
        code="ORG001",
        name="Test Organization",
        tenant=tenant,
    )

    user = User(
        username="member001",
        email="member001@example.com",
        password_hash="test-password-hash",
        first_name="Test",
        last_name="Member",
    )

    membership = OrganizationMembership(
        user=user,
        organization=organization,
    )

    session.add(membership)
    session.commit()

    persisted = session.get(
        OrganizationMembership,
        membership.id,
    )

    assert persisted is not None
    assert persisted.user_id == user.id
    assert persisted.organization_id == organization.id
    assert persisted.is_active is True

    assert persisted.user is user
    assert persisted.organization is organization


def test_organization_memberships_relationship(
    session,
):
    """
    Verify the Organization -> Membership relationship.
    """

    tenant = Tenant(
        code="TENANT001",
        name="Test Tenant",
    )

    organization = Organization(
        code="ORG001",
        name="Test Organization",
        tenant=tenant,
    )

    user_one = User(
        username="member001",
        email="member001@example.com",
        password_hash="hash-one",
        first_name="Member",
        last_name="One",
    )

    user_two = User(
        username="member002",
        email="member002@example.com",
        password_hash="hash-two",
        first_name="Member",
        last_name="Two",
    )

    membership_one = OrganizationMembership(
        user=user_one,
        organization=organization,
    )

    membership_two = OrganizationMembership(
        user=user_two,
        organization=organization,
    )

    session.add_all(
        [
            membership_one,
            membership_two,
        ]
    )

    session.commit()

    assert len(organization.memberships) == 2
    assert membership_one in organization.memberships
    assert membership_two in organization.memberships


def test_user_organization_memberships_relationship(
    session,
):
    """
    Verify the User -> Organization Membership relationship.
    """

    tenant = Tenant(
        code="TENANT001",
        name="Test Tenant",
    )

    organization = Organization(
        code="ORG001",
        name="Test Organization",
        tenant=tenant,
    )

    user = User(
        username="member001",
        email="member001@example.com",
        password_hash="test-password-hash",
        first_name="Test",
        last_name="Member",
    )

    membership = OrganizationMembership(
        user=user,
        organization=organization,
    )

    session.add(membership)
    session.commit()

    assert len(user.organization_memberships) == 1
    assert membership in user.organization_memberships


def test_duplicate_user_organization_membership_is_rejected(
    session,
):
    """
    Verify that a user cannot have duplicate membership
    records for the same organization.
    """

    tenant = Tenant(
        code="TENANT001",
        name="Test Tenant",
    )

    organization = Organization(
        code="ORG001",
        name="Test Organization",
        tenant=tenant,
    )

    user = User(
        username="member001",
        email="member001@example.com",
        password_hash="test-password-hash",
        first_name="Test",
        last_name="Member",
    )

    first = OrganizationMembership(
        user=user,
        organization=organization,
    )

    session.add(first)
    session.commit()

    second = OrganizationMembership(
        user=user,
        organization=organization,
    )

    session.add(second)

    with pytest.raises(IntegrityError):
        session.commit()

    session.rollback()


# ------------------------------------------------------------------
# Cascade Integrity
# ------------------------------------------------------------------


def test_deleting_tenant_cascades_to_organizations(
    session,
):
    """
    Verify that deleting a tenant removes its organizations.
    """

    tenant = Tenant(
        code="TENANT001",
        name="Test Tenant",
    )

    organization = Organization(
        code="ORG001",
        name="Test Organization",
        tenant=tenant,
    )

    session.add(organization)
    session.commit()

    organization_id = organization.id

    session.delete(tenant)
    session.commit()

    assert session.get(
        Organization,
        organization_id,
    ) is None


def test_deleting_organization_cascades_to_memberships(
    session,
):
    """
    Verify that deleting an organization removes its memberships.
    """

    tenant = Tenant(
        code="TENANT001",
        name="Test Tenant",
    )

    organization = Organization(
        code="ORG001",
        name="Test Organization",
        tenant=tenant,
    )

    user = User(
        username="member001",
        email="member001@example.com",
        password_hash="test-password-hash",
        first_name="Test",
        last_name="Member",
    )

    membership = OrganizationMembership(
        user=user,
        organization=organization,
    )

    session.add(membership)
    session.commit()

    membership_id = membership.id

    session.delete(organization)
    session.commit()

    assert session.get(
        OrganizationMembership,
        membership_id,
    ) is None
