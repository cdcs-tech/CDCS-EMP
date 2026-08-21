"""
CDCS Enterprise Management Platform (CDCS-EMP)

Reporting Framework

Public reporting contract surface.

This module provides a stable, explicit contract boundary
for the reporting framework.

The implementation modules remain responsible for their
individual contracts, while this module provides a single
framework-level import surface without introducing
additional runtime behaviour.
"""

from __future__ import annotations


# ---------------------------------------------------------
# Report Definition Contracts
# ---------------------------------------------------------

from app.core.reporting.models import (
    ReportDefinition,
    ReportParameter as ReportDefinitionParameter,
    ReportParameterCollection as ReportDefinitionParameterCollection,
)


# ---------------------------------------------------------
# Report Parameter Contracts
# ---------------------------------------------------------

from app.core.reporting.parameters import (
    ReportParameterType,
    ReportParameter,
    ReportParameterCollection,
)

# ---------------------------------------------------------
# Report Query Contracts
# ---------------------------------------------------------

from app.core.reporting.queries import (
    ReportQuery,
)


# ---------------------------------------------------------
# Report Provider Contracts
# ---------------------------------------------------------

from app.core.reporting.providers import (
    ReportProvider,
)


# ---------------------------------------------------------
# Report Result Contracts
# ---------------------------------------------------------

from app.core.reporting.results import (
    ReportResultStatus,
    ReportResult,
)



__all__ = [
    # Report Definition

    "ReportDefinition",

    "ReportDefinitionParameter",

    "ReportDefinitionParameterCollection",


    # Report Parameters

    "ReportParameterType",

    "ReportParameter",

    "ReportParameterCollection",


    "ReportQuery",


    # Providers

    "ReportProvider",


    # Results

    "ReportResultStatus",

    "ReportResult",
]
