"""
Database Connection Test
"""

from app import create_app
from app.extensions import db


def test_database_connection():
    app = create_app()

    with app.app_context():
        with db.engine.connect() as connection:
            assert connection is not None
