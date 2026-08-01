"""
Authentication Session Tests
"""
import pytest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.authentication,
]

def test_login_page(client):
    response = client.get("/auth/login")

    assert response.status_code == 200


def test_dashboard_requires_login(client):
    response = client.get(
        "/",
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]
