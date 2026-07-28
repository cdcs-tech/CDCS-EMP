from app.models import User


def test_password_hashing():
    user = User(
        username="admin",
        email="admin@example.com",
        first_name="System",
        last_name="Administrator",
    )

    user.set_password("Password123!")

    assert user.password_hash != "Password123!"
    assert user.check_password("Password123!")
    assert not user.check_password("WrongPassword")


def test_full_name():
    user = User(
        username="moses",
        email="moses@example.com",
        first_name="Moses",
        last_name="Schole",
    )

    assert user.full_name == "Moses Schole"
