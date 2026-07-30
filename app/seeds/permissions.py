"""
CDCS Enterprise Management Platform (CDCS-EMP)

Permission Seeder
"""

from app.extensions import db
from app.models import Permission


DEFAULT_PERMISSIONS = [

    {
        "name": "system.admin",
        "module": "System",
        "description": "Full system administration access",
    },

    {
        "name": "dashboard.view",
        "module": "Dashboard",
        "description": "View dashboard",
    },

    {
        "name": "users.create",
        "module": "Users",
        "description": "Create users",
    },

    {
        "name": "users.read",
        "module": "Users",
        "description": "Read users",
    },

    {
        "name": "users.update",
        "module": "Users",
        "description": "Update users",
    },

    {
        "name": "users.delete",
        "module": "Users",
        "description": "Delete users",
    },

]


def seed_permissions():

    for item in DEFAULT_PERMISSIONS:

        permission = Permission.query.filter_by(
            name=item["name"]
        ).first()

        if permission is None:

            permission = Permission(

                name=item["name"],

                module=item["module"],

                description=item["description"],

            )

            db.session.add(permission)

    db.session.commit()
