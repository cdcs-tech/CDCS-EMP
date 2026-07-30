"""
CDCS Enterprise Management Platform (CDCS-EMP)

Administrator User Seeder
"""


from app.models import User

from .base import BaseSeeder

from .constants import (
    ADMIN_USERNAME,
    ADMIN_EMAIL,
    ADMIN_FIRST_NAME,
    ADMIN_LAST_NAME,
    ADMIN_DEFAULT_PASSWORD,
)



class UserSeeder(BaseSeeder):
    """
    Seeds default platform users.

    Safe to execute multiple times.
    """


    name = "User Seeder"



    def run(self):

        created = 0
        skipped = 0


        self.log("Starting...")


        existing = User.query.filter(

            (
                User.username == ADMIN_USERNAME
            )
            |
            (
                User.email == ADMIN_EMAIL
            )

        ).first()



        if existing:

            skipped += 1


        else:

            user = User(

                username=ADMIN_USERNAME,

                email=ADMIN_EMAIL,

                first_name=ADMIN_FIRST_NAME,

                last_name=ADMIN_LAST_NAME,

                is_active=True,

            )


            user.set_password(
                ADMIN_DEFAULT_PASSWORD
            )


            self.add(user)

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
