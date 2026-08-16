"""
CDCS Enterprise Management Platform (CDCS-EMP)

Organization Membership Model Unit Tests
"""

from app.models.organization_membership import (
    OrganizationMembership,
)


def test_membership_can_be_constructed():
    """
    Verify that an organization membership can be
    constructed with the required domain attributes.
    """

    membership = OrganizationMembership(
        organization_id=1,
        user_id=1,
    )

    assert membership.organization_id == 1
    assert membership.user_id == 1


def test_membership_is_active_has_default():
    """
    Verify that the is_active column defines
    a True default.

    SQLAlchemy applies the default during INSERT/flush,
    rather than necessarily assigning it immediately
    during Python object construction.
    """

    column = OrganizationMembership.__table__.c.is_active

    assert column.default is not None
    assert column.default.arg is True
