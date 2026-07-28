"""
RBAC Tests
"""


def test_user_has_role():

    from app.models import User

    user = User()

    assert hasattr(
        user,
        "has_role"
    )


def test_user_has_permission():

    from app.models import User

    user = User()

    assert hasattr(
        user,
        "has_permission"
    )
