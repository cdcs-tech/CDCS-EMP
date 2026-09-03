import pytest

from app.core.security.module_permissions import (
    ModulePermissionSynchronizer,
)
from app.core.security.permissions import (
    Permission,
)
from app.models import (
    Permission as DBPermission,
    Role,
    RolePermission,
)


class FakeModule:
    def __init__(self, permissions):
        self._permissions = permissions

    def get_permissions(self):
        return list(self._permissions)


@pytest.fixture
def system_administrator(db_session):
    role = Role(
        name="System Administrator",
        description="System Administrator",
        is_system=True,
    )

    db_session.add(role)
    db_session.commit()

    return role


def test_synchronizer_creates_missing_permission_and_assignment(
    db_session,
    system_administrator,
):
    permission = Permission(
        code="TEST.MODULE.READ",
        name="test.module.read",
        description="Read Test Module.",
        module="TEST",
        resource="module",
        action="read",
    )

    module = FakeModule([permission])

    synchronizer = ModulePermissionSynchronizer()

    created = synchronizer.synchronize([module])

    assert created == 2

    db_permission = DBPermission.query.filter_by(
        name="test.module.read"
    ).first()

    assert db_permission is not None
    assert db_permission.module == "TEST"
    assert (
        db_permission.description
        == "Read Test Module."
    )

    assignment = RolePermission.query.filter_by(
        role_id=system_administrator.id,
        permission_id=db_permission.id,
    ).first()

    assert assignment is not None


def test_synchronizer_is_idempotent(
    db_session,
    system_administrator,
):
    permission = Permission(
        code="TEST.MODULE.READ",
        name="test.module.read",
        description="Read Test Module.",
        module="TEST",
        resource="module",
        action="read",
    )

    module = FakeModule([permission])

    synchronizer = ModulePermissionSynchronizer()

    first_created = synchronizer.synchronize([module])
    second_created = synchronizer.synchronize([module])

    assert first_created == 2
    assert second_created == 0

    assert (
        DBPermission.query.filter_by(
            name="test.module.read"
        ).count()
        == 1
    )

    assert (
        RolePermission.query.join(
            DBPermission
        )
        .filter(
            RolePermission.role_id
            == system_administrator.id,
            DBPermission.name
            == "test.module.read",
        )
        .count()
        == 1
    )


def test_synchronizer_preserves_existing_permission_and_assignment(
    db_session,
    system_administrator,
):
    permission = DBPermission(
        name="test.module.read",
        module="TEST",
        description="Existing permission.",
    )

    db_session.add(permission)
    db_session.flush()

    assignment = RolePermission(
        role_id=system_administrator.id,
        permission_id=permission.id,
    )

    db_session.add(assignment)
    db_session.commit()

    module_permission = Permission(
        code="TEST.MODULE.READ",
        name="test.module.read",
        description="New description that must not overwrite existing data.",
        module="TEST",
        resource="module",
        action="read",
    )

    synchronizer = ModulePermissionSynchronizer()

    created = synchronizer.synchronize(
        [FakeModule([module_permission])]
    )

    assert created == 0

    refreshed_permission = DBPermission.query.filter_by(
        name="test.module.read"
    ).first()

    assert refreshed_permission.description == "Existing permission."

    assert (
        RolePermission.query.filter_by(
            role_id=system_administrator.id,
            permission_id=refreshed_permission.id,
        ).count()
        == 1
    )


def test_synchronizer_creates_missing_assignment_for_existing_permission(
    db_session,
    system_administrator,
):
    permission = DBPermission(
        name="test.module.read",
        module="TEST",
        description="Existing permission.",
    )

    db_session.add(permission)
    db_session.commit()

    module_permission = Permission(
        code="TEST.MODULE.READ",
        name="test.module.read",
        description="Existing permission.",
        module="TEST",
        resource="module",
        action="read",
    )

    synchronizer = ModulePermissionSynchronizer()

    created = synchronizer.synchronize(
        [FakeModule([module_permission])]
    )

    assert created == 1

    assert (
        RolePermission.query.filter_by(
            role_id=system_administrator.id,
            permission_id=permission.id,
        ).count()
        == 1
    )


def test_synchronizer_rejects_missing_system_administrator(
    db_session,
):
    permission = Permission(
        code="TEST.MODULE.READ",
        name="test.module.read",
        description="Read Test Module.",
        module="TEST",
        resource="module",
        action="read",
    )

    synchronizer = ModulePermissionSynchronizer()

    with pytest.raises(
        ValueError,
        match="Role not found: System Administrator",
    ):
        synchronizer.synchronize(
            [FakeModule([permission])]
        )
