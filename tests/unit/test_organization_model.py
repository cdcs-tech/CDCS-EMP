"""
CDCS Enterprise Management Platform (CDCS-EMP)

Organization Model Unit Tests
"""

from app.models.organization import Organization


def test_organization_can_be_constructed():
    """
    Verify that an organization can be constructed
    with the required domain attributes.
    """

    organization = Organization(
        code="CDCS",
        name="CDCS Enterprise",
    )

    assert organization.code == "CDCS"
    assert organization.name == "CDCS Enterprise"


def test_organization_is_active_has_default():
    """
    Verify that the is_active column defines
    a True default.

    SQLAlchemy applies the default during INSERT/flush,
    rather than necessarily assigning it immediately
    during Python object construction.
    """

    column = Organization.__table__.c.is_active

    assert column.default is not None
    assert column.default.arg is True
