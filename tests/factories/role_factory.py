"""
Role Factory
"""

from app.models.role import Role


class RoleFactory:
    """
    Factory for creating Role objects.
    """

    @staticmethod
    def create(
        session,
        name="User",
        description="Standard user role",
        is_system=False,
        commit=True,
    ):
        role = Role(
            name=name,
            description=description,
            is_system=is_system,
        )

        session.add(role)

        if commit:
            session.commit()

        return role
