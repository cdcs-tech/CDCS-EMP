"""
Authorization Tests
"""

from app.security.authorization import AuthorizationService


def test_authorization_service_exists():
    assert AuthorizationService is not None


def test_has_permissions_method_exists():
    assert hasattr(
        AuthorizationService,
        "has_permissions",
    )
