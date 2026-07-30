"""
CDCS Enterprise Management Platform (CDCS-EMP)

User Role Seeder
"""


from app.models import (
    User,
    Role,
    UserRole,
)

from .base import BaseSeeder

from .constants import (
    ADMIN_USERNAME,
    SYSTEM_ADMINISTRATOR,
)



class UserRoleSeeder(BaseSeeder):
    """
    Assigns roles to users.

    Safe to execute multiple times.
    """


    name = "User Role Seeder"



    def run(self):

        created = 0
        skipped = 0


        self.log("Starting...")



        user = self.exists(
            User,
            username=ADMIN_USERNAME,
        )


        if not user:

            raise Exception(
                f"User not found: "
                f"{ADMIN_USERNAME}"
            )



        role = self.exists(
            Role,
            name=SYSTEM_ADMINISTRATOR,
        )


        if not role:

            raise Exception(
                f"Role not found: "
                f"{SYSTEM_ADMINISTRATOR}"
            )



        existing = UserRole.query.filter_by(

            user_id=user.id,

            role_id=role.id,

        ).first()



        if existing:

            skipped += 1


        else:

            user_role = UserRole(

                user_id=user.id,

                role_id=role.id,

            )


            self.add(user_role)

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
