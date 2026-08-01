"""
User Fixtures
"""

import pytest

from app.models.user import User


@pytest.fixture(scope="function")
def admin_user(session):
    """
    Create an administrator user.
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


@pytest.fixture(scope="function")
def regular_user(session):
    """
    Create a standard user.
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
