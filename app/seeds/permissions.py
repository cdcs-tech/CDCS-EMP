"""
CDCS Enterprise Management Platform (CDCS-EMP)

Permission Seeder
"""

from app.models import Permission

from .base import BaseSeeder
from .constants import PERMISSIONS


class PermissionSeeder(BaseSeeder):
    """
    Seeds the system permissions.

    Safe to execute multiple times.
    """

    name = "Permission Seeder"

    def run(self):

        created = 0
        skipped = 0

        self.log("Starting...")

        for item in PERMISSIONS:

            existing = self.exists(
                Permission,
                name=item["name"],
            )

            if existing:

                skipped += 1
                continue

            permission = Permission(

                name=item["name"],

                module=item["module"],

                description=item["description"],

            )

            self.add(permission)

            created += 1

        self.commit()

        self.log(
            f"Created: {created}"
        )

        self.log(
            f"Skipped: {skipped}"
        )

        return {

            "created": created,

            "skipped": skipped,

        }
