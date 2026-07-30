"""
CDCS Enterprise Management Platform (CDCS-EMP)

Role Seeder
"""

from app.models import Role

from .base import BaseSeeder
from .constants import ROLES


class RoleSeeder(BaseSeeder):
    """
    Seeds default system roles.

    Safe to execute multiple times.
    """

    name = "Role Seeder"


    def run(self):

        created = 0
        skipped = 0

        self.log("Starting...")

        for item in ROLES:

            existing = self.exists(
                Role,
                name=item["name"],
            )

            if existing:

                skipped += 1
                continue


            role = Role(

                name=item["name"],

                description=item["description"],

                is_system=item["is_system"],

            )

            self.add(role)

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
