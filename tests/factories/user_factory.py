"""
User Factory
"""

from app.models.user import User
from app.models.user_role import UserRole
from app.models.role_permission import RolePermission

from tests.factories.permission_factory import PermissionFactory
from tests.factories.role_factory import RoleFactory


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
        Create a default administrator with dashboard access.
        """

        user = UserFactory.create(
            session=session,
            username="admin",
            email="admin@test.local",
            first_name="System",
            last_name="Administrator",
            password="Admin@123",
            commit=False,
        )

        role = RoleFactory.create(
            session=session,
            name="Administrator",
            description="System administrator role",
            is_system=True,
            commit=False,
        )

        permission = PermissionFactory.create(
            session=session,
            name="dashboard.view",
            module="Dashboard",
            description="View dashboard",
            commit=False,
        )

        role_permission = RolePermission(
            role=role,
            permission=permission,
        )

        user_role = UserRole(
            user=user,
            role=role,
        )

        session.add(role_permission)
        session.add(user_role)

        session.commit()

        return user
