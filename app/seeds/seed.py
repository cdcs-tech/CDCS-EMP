"""
Database Seeder
"""

from .permissions import seed_permissions
from .roles import seed_roles
from .users import seed_admin


def seed_database():

    seed_permissions()

    seed_roles()

    seed_admin()

    print(

        "Database successfully seeded."

    )
