"""
CDCS Enterprise Management Platform (CDCS-EMP)

Seed Constants
"""

# ==========================================================
# Roles
# ==========================================================

SYSTEM_ADMINISTRATOR = "System Administrator"

MANAGER = "Manager"

STAFF = "Staff"

# ==========================================================
# Role Definitions
# ==========================================================

ROLES = [

    {
        "name": SYSTEM_ADMINISTRATOR,
        "description": (
            "Full system administration access"
        ),
        "is_system": True,
    },

    {
        "name": MANAGER,
        "description": (
            "Operational management access"
        ),
        "is_system": True,
    },

    {
        "name": STAFF,
        "description": (
            "Standard staff access"
        ),
        "is_system": True,
    },

]

# ==========================================================
# Administrator Account
# ==========================================================

ADMIN_USERNAME = "admin"

ADMIN_EMAIL = "admin@cdcs.local"

ADMIN_FIRST_NAME = "System"

ADMIN_LAST_NAME = "Administrator"

ADMIN_DEFAULT_PASSWORD = "Admin@123"


# ==========================================================
# Permission Modules
# ==========================================================

MODULE_SYSTEM = "System"

MODULE_DASHBOARD = "Dashboard"

MODULE_USER = "User"

MODULE_ROLE = "Role"


# ==========================================================
# Permissions
# ==========================================================

PERMISSIONS = [

    {
        "module": MODULE_SYSTEM,
        "name": "system.admin",
        "description": "Full system administration",
    },

    {
        "module": MODULE_DASHBOARD,
        "name": "dashboard.view",
        "description": "View dashboard",
    },

    {
        "module": MODULE_USER,
        "name": "user.create",
        "description": "Create users",
    },

    {
        "module": MODULE_USER,
        "name": "user.read",
        "description": "View users",
    },

    {
        "module": MODULE_USER,
        "name": "user.update",
        "description": "Update users",
    },

    {
        "module": MODULE_USER,
        "name": "user.delete",
        "description": "Delete users",
    },

    {
        "module": MODULE_ROLE,
        "name": "role.create",
        "description": "Create roles",
    },

    {
        "module": MODULE_ROLE,
        "name": "role.read",
        "description": "View roles",
    },

    {
        "module": MODULE_ROLE,
        "name": "role.update",
        "description": "Update roles",
    },

    {
        "module": MODULE_ROLE,
        "name": "role.delete",
        "description": "Delete roles",
    },

]

# ==========================================================
# Role Permission Mapping
# ==========================================================


ROLE_PERMISSIONS = {

    SYSTEM_ADMINISTRATOR: [

        "system.admin",

        "dashboard.view",

        "user.create",

        "user.read",

        "user.update",

        "user.delete",

        "role.create",

        "role.read",

        "role.update",

        "role.delete",

    ],


    MANAGER: [

        "dashboard.view",

        "user.read",

        "user.update",

    ],


    STAFF: [

        "dashboard.view",

    ],

}
