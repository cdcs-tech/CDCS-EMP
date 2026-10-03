"""
CDCS Enterprise Management Platform (CDCS-EMP)

Finance Integration Contracts.

Defines Finance-owned enterprise integration identities while
reusing explicit source-owned business contracts.
"""

FINANCE_INTEGRATION_PROVIDER = "finance"

FINANCE_CATERING_REVENUE_OPERATION = (
    "consume_catering_revenue"
)


__all__ = [
    "FINANCE_INTEGRATION_PROVIDER",
    "FINANCE_CATERING_REVENUE_OPERATION",
]
