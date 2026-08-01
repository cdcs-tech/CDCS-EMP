"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Pytest Fixture Manager
"""

import sys
from pathlib import Path

import pytest

# -------------------------------------------------------
# Make project root importable
# -------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# -------------------------------------------------------
# Application Imports
# -------------------------------------------------------

from app import create_app
from app.extensions import db
from app.models.user import User

# -------------------------------------------------------
# Application Fixture
# -------------------------------------------------------

@pytest.fixture(scope="function")
def app():
    """
    Create a testing application.
    """

    app = create_app("testing")

    with app.app_context():

        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


# -------------------------------------------------------
# Test Client
# -------------------------------------------------------

@pytest.fixture(scope="function")
def client(app):
    """
    Flask test client.
    """

    return app.test_client()


# -------------------------------------------------------
# CLI Runner
# -------------------------------------------------------

@pytest.fixture(scope="function")
def runner(app):
    """
    Flask CLI runner.
    """

    return app.test_cli_runner()


# -------------------------------------------------------
# Database Session
# -------------------------------------------------------

@pytest.fixture(scope="function")
def session(app):
    """
    Database session.
    """

    yield db.session

    db.session.rollback()


# -------------------------------------------------------
# Administrator Fixture
# -------------------------------------------------------

@pytest.fixture(scope="function")
def admin_user(session):
    """
    Create administrator.
    """

    user = User(
        username="admin",
        email="admin@test.local",
        first_name="System",
        last_name="Administrator",
    )

    user.set_password("Admin@123")

    session.add(user)
    session.commit()

    return user


# -------------------------------------------------------
# Standard User Fixture
# -------------------------------------------------------

@pytest.fixture(scope="function")
def regular_user(session):
    """
    Create standard user.
    """

    user = User(
        username="john",
        email="john@test.local",
        first_name="John",
        last_name="Doe",
    )

    user.set_password("Password123")

    session.add(user)
    session.commit()

    return user


# -------------------------------------------------------
# Authenticated Client
# -------------------------------------------------------

@pytest.fixture(scope="function")
def authenticated_client(
    client,
    admin_user,
):
    """
    Login administrator.
    """

    client.post(
        "/auth/login",
        data={
            "username": admin_user.username,
            "password": "Admin@123",
        },
        follow_redirects=True,
    )

    return client
