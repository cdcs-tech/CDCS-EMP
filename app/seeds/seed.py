"""
CDCS Enterprise Management Platform (CDCS-EMP)

Seed Orchestrator
"""


from .permissions import PermissionSeeder
from .roles import RoleSeeder
from .role_permissions import RolePermissionSeeder
from .module_permissions import ModulePermissionSeeder
from .users import UserSeeder
from .user_roles import UserRoleSeeder



class SeedManager:
    """
    Controls execution order of all seeders.
    """


    def __init__(self):

        self.seeders = [

            PermissionSeeder(),

            RoleSeeder(),

            RolePermissionSeeder(),

            ModulePermissionSeeder(),

            UserSeeder(),

            UserRoleSeeder(),

        ]


    def run(self):

        results = {}


        for seeder in self.seeders:

            results[
                seeder.name
            ] = seeder.run()


        return results
