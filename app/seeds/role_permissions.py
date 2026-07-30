"""
CDCS Enterprise Management Platform (CDCS-EMP)

Role Permission Seeder
"""


from app.models import (
    Role,
    Permission,
    RolePermission,
)

from .base import BaseSeeder
from .constants import ROLE_PERMISSIONS



class RolePermissionSeeder(BaseSeeder):
    """
    Seeds role-permission relationships.

    Safe to execute multiple times.
    """


    name = "Role Permission Seeder"



    def run(self):

        created = 0
        skipped = 0


        self.log("Starting...")


        for role_name, permissions in ROLE_PERMISSIONS.items():


            role = self.exists(
                Role,
                name=role_name,
            )


            if not role:

                raise Exception(
                    f"Role not found: {role_name}"
                )



            for permission_name in permissions:


                permission = self.exists(
                    Permission,
                    name=permission_name,
                )


                if not permission:

                    raise Exception(
                        f"Permission not found: "
                        f"{permission_name}"
                    )



                existing = RolePermission.query.filter_by(

                    role_id=role.id,

                    permission_id=permission.id,

                ).first()



                if existing:

                    skipped += 1

                    continue



                mapping = RolePermission(

                    role_id=role.id,

                    permission_id=permission.id,

                )


                self.add(mapping)

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
