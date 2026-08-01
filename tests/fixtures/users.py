"""
User Fixtures
"""

import pytest

from tests.factories.user_factory import UserFactory


@pytest.fixture(scope="function")
def admin_user(session):
    return UserFactory.create_admin(session)


@pytest.fixture(scope="function")
def regular_user(session):
    return UserFactory.create(session)
