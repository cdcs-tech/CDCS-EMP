import pytest

from app.core.security.permissions import Permission
from app.models import Permission as DBPermission
from app.models import Role, RolePermission
from app.seeds.module_permissions import ModulePermissionSeeder
from app.seeds.seed import SeedManager


class FakeModule:
    def __init__(self, permissions):
        self._permissions = permissions

    def get_permissions(self):
        return list(self._permissions)


class FakeModuleManager:
    def __init__(self, modules):
        self._modules = modules

    def get_active_modules(self):
        return list(self._modules)


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


@pytest.fixture
def module_permission():
    return Permission(
        code="TEST.MODULE.READ",
        name="test.module.read",
        description="Read Test Module.",
        module="TEST",
        resource="module",
        action="read",
    )


def test_module_permission_seeder_synchronizes_loaded_modules(
    app,
    db_session,
    system_administrator,
    module_permission,
):
    module = FakeModule([module_permission])

    app.extensions["module_manager"] = FakeModuleManager(
        [module]
    )

    seeder = ModulePermissionSeeder()

    result = seeder.run()

    assert result == {
        "created": 2,
        "skipped": 0,
    }

    db_permission = DBPermission.query.filter_by(
        name="test.module.read"
    ).first()

    assert db_permission is not None
    assert db_permission.module == "TEST"
    assert db_permission.description == "Read Test Module."

    assignment = RolePermission.query.filter_by(
        role_id=system_administrator.id,
        permission_id=db_permission.id,
    ).first()

    assert assignment is not None


def test_module_permission_seeder_is_idempotent(
    app,
    db_session,
    system_administrator,
    module_permission,
):
    module = FakeModule([module_permission])

    app.extensions["module_manager"] = FakeModuleManager(
        [module]
    )

    seeder = ModulePermissionSeeder()

    first_result = seeder.run()
    second_result = seeder.run()

    assert first_result == {
        "created": 2,
        "skipped": 0,
    }

    assert second_result == {
        "created": 0,
        "skipped": 0,
    }

    assert (
        DBPermission.query.filter_by(
            name="test.module.read"
        ).count()
        == 1
    )

    assert (
        RolePermission.query.join(DBPermission)
        .filter(
            RolePermission.role_id
            == system_administrator.id,
            DBPermission.name
            == "test.module.read",
        )
        .count()
        == 1
    )


def test_module_permission_seeder_requires_module_manager(
    app,
    db_session,
    system_administrator,
):
    app.extensions.pop(
        "module_manager",
        None,
    )

    seeder = ModulePermissionSeeder()

    with pytest.raises(
        RuntimeError,
        match="Module manager is not available.",
    ):
        seeder.run()


def test_seed_manager_places_module_permission_seeder_after_core_rbac(
    app,
):
    manager = SeedManager()

    names = [
        seeder.name
        for seeder in manager.seeders
    ]

    assert names.index("Role Permission Seeder") < names.index(
        "Module Permission Seeder"
    )

    assert names.index("Module Permission Seeder") < names.index(
        "User Seeder"
    )
