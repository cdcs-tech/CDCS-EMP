"""
CDCS-EMP Extension Registry

Exports all Flask extension instances.
"""

from .database import db
from .migrate import migrate
from .login import login_manager
from .bcrypt import bcrypt
from .csrf import csrf

__all__ = [
    "db",
    "migrate",
    "login_manager",
    "bcrypt",
    "csrf",
]