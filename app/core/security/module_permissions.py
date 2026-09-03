"""
CDCS Enterprise Management Platform (CDCS-EMP)

Module Permission Synchronization.

Synchronizes permissions declared by enterprise modules
into the database-backed application RBAC model.
"""

from __future__ import annotations

from collections.abc import Iterable

from app.extensions import db
from app.models import (
    Permission as DBPermission,
    Role,
    RolePermission,
)

from app.core.security.permissions import (
    Permission,
)


SYSTEM_ADMINISTRATOR_ROLE = "System Administrator"


class ModulePermissionSynchronizer:
    """
    Synchronize enterprise module permissions with
    the database-backed RBAC model.

    Synchronization is intentionally additive and idempotent.

    Existing permissions and role assignments are preserved.
    Missing module permissions are created and assigned to
    the System Administrator role.

    The caller owns the transaction boundary.
    """

    def __init__(
        self,
        role_name: str = SYSTEM_ADMINISTRATOR_ROLE,
    ) -> None:
        self.role_name = role_name

    def synchronize(
        self,
        modules: Iterable[object],
    ) -> int:
        """
        Synchronize permissions exposed by the supplied modules.

        Args:
            modules:
                Enterprise modules exposing ``get_permissions()``.

        Returns:
            Number of database records created.

        Raises:
            ValueError:
                When the System Administrator role does not exist.
        """

        role = Role.query.filter_by(
            name=self.role_name
        ).first()

        if role is None:
            raise ValueError(
                f"Role not found: {self.role_name}"
            )

        created = 0

        for module in modules:
            permissions = module.get_permissions()

            for permission in permissions:
                if not isinstance(
                    permission,
                    Permission,
                ):
                    continue

                db_permission = (
                    DBPermission.query.filter_by(
                        name=permission.name
                    ).first()
                )

                if db_permission is None:
                    db_permission = DBPermission(
                        name=permission.name,
                        module=permission.module,
                        description=permission.description,
                    )

                    db.session.add(
                        db_permission
                    )

                    db.session.flush()

                    created += 1

                assignment = (
                    RolePermission.query.filter_by(
                        role_id=role.id,
                        permission_id=db_permission.id,
                    ).first()
                )

                if assignment is None:
                    db.session.add(
                        RolePermission(
                            role_id=role.id,
                            permission_id=db_permission.id,
                        )
                    )

                    created += 1

        return created


__all__ = [
    "SYSTEM_ADMINISTRATOR_ROLE",
    "ModulePermissionSynchronizer",
]
