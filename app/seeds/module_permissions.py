"""
CDCS Enterprise Management Platform (CDCS-EMP)

Module Permission Seeder
"""

from flask import current_app

from app.core.security import ModulePermissionSynchronizer

from .base import BaseSeeder


class ModulePermissionSeeder(BaseSeeder):
    """
    Synchronize permissions declared by loaded enterprise modules.

    Module permissions are synchronized after core RBAC roles and
    permissions have been seeded.
    """

    name = "Module Permission Seeder"

    def run(self):
        module_manager = current_app.extensions.get(
            "module_manager"
        )

        if module_manager is None:
            raise RuntimeError(
                "Module manager is not available."
            )

        modules = module_manager.get_active_modules()

        synchronizer = ModulePermissionSynchronizer()

        created = synchronizer.synchronize(
            modules
        )

        if created:
            self.commit()

        return {
            "created": created,
            "skipped": 0,
        }
