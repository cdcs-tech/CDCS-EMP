"""
CDCS Enterprise Management Platform (CDCS-EMP)

Tenant Model Unit Tests
"""

from app.models.tenant import Tenant


def test_tenant_can_be_constructed():
    """
    Verify that a tenant can be constructed
    with the required domain attributes.
    """

    tenant = Tenant(
        code="CDCS",
        name="CDCS Enterprise",
    )

    assert tenant.code == "CDCS"
    assert tenant.name == "CDCS Enterprise"


def test_tenant_is_active_has_default():
    """
    Verify that the is_active column defines
    a True default.

    SQLAlchemy applies the default during INSERT/flush,
    rather than necessarily assigning it immediately
    during Python object construction.
    """

    column = Tenant.__table__.c.is_active

    assert column.default is not None
    assert column.default.arg is True
