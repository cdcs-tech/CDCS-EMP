from app.extensions import db
from app.models import Role

DEFAULT_ROLES = [

    "System Administrator",

    "Manager",

    "Staff",

]


def seed_roles():

    for role_name in DEFAULT_ROLES:

        role = Role.query.filter_by(
            name=role_name
        ).first()

        if role is None:

            db.session.add(

                Role(
                    name=role_name
                )

            )

    db.session.commit()
