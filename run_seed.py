"""
CDCS Enterprise Management Platform (CDCS-EMP)

Database Seed Runner
"""

from app import create_app

from app.seeds.permissions import PermissionSeeder
from app.seeds.roles import RoleSeeder
from app.seeds.role_permissions import RolePermissionSeeder
from app.seeds.users import UserSeeder


app = create_app()


with app.app_context():

    print("\n")
    print("=" * 50)
    print("CDCS-EMP Database Seeder")
    print("=" * 50)


    PermissionSeeder().run()

    RoleSeeder().run()

    RolePermissionSeeder().run()

    UserSeeder().run()


    print("=" * 50)
    print("Seeding completed.")
    print("=" * 50)
