"""
Authentication Session Tests
"""

import pytest

from tests.utils.assertions import (
    assert_redirect,
    assert_success,
)

pytestmark = [
    pytest.mark.integration,
    pytest.mark.authentication,
]


def test_login_page(client):
    """
    Verify that the login page is accessible.
    """

    response = client.get("/auth/login")

    assert_success(response)


def test_dashboard_requires_login(client):
    """
    Verify that anonymous users are redirected
    to the login page.
    """

    response = client.get(
        "/",
        follow_redirects=False,
    )

    assert_redirect(
        response,
        "/auth/login",
    )
