"""
Permission Factory
"""

from app.models.permission import Permission


class PermissionFactory:
    """
    Factory for creating Permission objects.
    """

    @staticmethod
    def create(
        session,
        name="dashboard.view",
        module="Dashboard",
        description="View dashboard",
        commit=True,
    ):
        permission = Permission(
            name=name,
            module=module,
            description=description,
        )

        session.add(permission)

        if commit:
            session.commit()

        return permission
