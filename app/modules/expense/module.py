"""
CDCS Enterprise Management Platform (CDCS-EMP)

Expense Management Business Module
"""

from app.core.modules import (
    BaseModule,
    ModuleMetadata,
)

from app.modules.expense.security import (
    EXPENSE_PERMISSIONS,
)


class ExpenseModule(BaseModule):
    """
    CDCS-EMP Expense Management business module.

    Provides the enterprise module boundary for reusable
    operational expense management.
    """

    def register_models(self, app):
        """
        Register Expense Management SQLAlchemy models.

        Importing the module-local model package ensures
        Expense models are attached to the existing SQLAlchemy
        metadata without exposing them through app.models.
        """

        from app.modules.expense.models import (
            Expense,
            ExpenseClassification,
        )

        # Keep explicit references so the imports are intentional
        # and remain visible to static analysis.
        _ = (
            ExpenseClassification,
            Expense,
        )

    def get_metadata(self) -> ModuleMetadata:
        """
        Return Expense Management module metadata.
        """

        return ModuleMetadata(
            code="EXPENSE",
            name="Expense Management",
            description=(
                "Reusable operational expense management "
                "capability for enterprise business operations."
            ),
            version="1.0.0",
            author="CDCS",
            category="Business",
            icon="bi-receipt",
            url_prefix="/expense",
            dependencies=[],
            permissions=[],
            navigation_enabled=True,
            dashboard_enabled=False,
            active=True,
        )

    def get_permissions(self):
        """
        Return Expense Management enterprise security permissions.

        Permission registration is delegated to the enterprise
        BaseModule lifecycle.
        """

        return list(
            EXPENSE_PERMISSIONS
        )

    def register_blueprints(self, app):
        """
        Register the Expense Management HTTP blueprint.

        The blueprint is registered through the Enterprise
        Module Framework lifecycle.
        """

        from app.modules.expense.routes import (
            expense_bp,
        )

        app.register_blueprint(
            expense_bp,
            url_prefix=self.metadata.url_prefix,
        )


__all__ = [
    "ExpenseModule",
]
