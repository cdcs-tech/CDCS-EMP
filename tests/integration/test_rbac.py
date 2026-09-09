"""
RBAC Tests
"""
import pytest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.authorization,
]

def test_user_has_role():

    from app.models import User

    user = User()

    assert hasattr(
        user,
        "has_role"
    )


def test_user_has_permission():

    from app.models import User

    user = User()

    assert hasattr(
        user,
        "has_permission"
    )
def test_user_has_permission_accepts_canonical_permission_code():

    from app.models import (
        Permission,
        Role,
        RolePermission,
        User,
        UserRole,
    )

    permission = Permission(
        name="catering.stock_movement.create",
        module="CATERING",
        description="Create Catering stock movements.",
    )

    role = Role(
        name="System Administrator",
        description="System administrator role.",
        is_system=True,
    )

    role_permission = RolePermission(
        role=role,
        permission=permission,
    )

    role.role_permissions = [role_permission]

    user = User()

    user_role = UserRole(
        user=user,
        role=role,
    )

    user.user_roles = [user_role]

    assert user.has_permission(
        "CATERING.STOCK_MOVEMENT.CREATE"
    ) is True

