"""
User Factory
"""

from app.models.user import User


class UserFactory:
    """
    Factory for creating User objects.
    """

    DEFAULT_PASSWORD = "Password123"

    @staticmethod
    def create(
        session,
        username="john",
        email="john@test.local",
        first_name="John",
        last_name="Doe",
        password=None,
        commit=True,
    ):
        """
        Create and optionally persist a user.
        """

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(
            password or UserFactory.DEFAULT_PASSWORD
        )

        session.add(user)

        if commit:
            session.commit()

        return user

    @staticmethod
    def create_admin(session):
        """
        Create a default administrator.
        """

        return UserFactory.create(
            session=session,
            username="admin",
            email="admin@test.local",
            first_name="System",
            last_name="Administrator",
            password="Admin@123",
        )
