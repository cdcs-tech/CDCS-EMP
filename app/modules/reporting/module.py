"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Enterprise Module
"""

from app.core.modules import (
    BaseModule,
    ModuleMetadata,
)

from app.core.reporting.permissions import (
    all_report_permissions,
)


class ReportingModule(BaseModule):
    """
    Enterprise module boundary for reporting capabilities.

    Reporting owns report-level access and execution
    capabilities. Domain modules remain responsible for
    their own business data and calculations.
    """

    def get_metadata(self) -> ModuleMetadata:
        """Return Reporting enterprise module metadata."""

        return ModuleMetadata(
            code="REPORTING",
            name="Reporting",
            description=(
                "Enterprise reporting and analytics capabilities."
            ),
            version="1.0.0",
            author="CDCS",
            category="Business",
            icon="bi-graph-up",
            url_prefix="/reports",
            dependencies=[],
            permissions=[],
            navigation_enabled=False,
            dashboard_enabled=False,
            active=True,
        )

    def get_permissions(self):
        """Return the canonical Reporting permissions."""

        return list(all_report_permissions())

    def register_blueprints(self, app):
        """Register the Reporting HTTP blueprint."""

        from app.modules.reporting.routes import (
            reporting_bp,
        )

        app.register_blueprint(
            reporting_bp,
            url_prefix=self.metadata.url_prefix,
        )


__all__ = [
    "ReportingModule",
]
