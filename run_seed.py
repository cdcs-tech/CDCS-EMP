"""
CDCS Enterprise Management Platform (CDCS-EMP)

Database Seed Runner
"""

from app import create_app
from app.seeds.permissions import PermissionSeeder

app = create_app()

with app.app_context():
    PermissionSeeder().run()
