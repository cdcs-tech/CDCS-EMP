"""
CDCS Enterprise Management Platform (CDCS-EMP)

Enterprise Security Framework

Security audit event definitions.
"""


from dataclasses import dataclass, field

from datetime import datetime, timezone

from typing import Dict, Any



@dataclass
class SecurityAuditEvent:
    """
    Represents a security-related event.

    Audit events provide traceability for
    authentication, authorization and
    governance activities.
    """

    event_type: str

    subject: str = ""

    resource: str = ""

    action: str = ""

    result: str = "SUCCESS"

    message: str = ""

    metadata: Dict[
        str,
        Any
    ] = field(
        default_factory=dict
    )

    timestamp: datetime = field(
        default_factory=lambda:
            datetime.now(
                timezone.utc
            )
    )



    def __post_init__(self):
        """
        Validate audit event.
        """

        if not self.event_type:

            raise ValueError(
                "Audit event type is required."
            )



    def is_success(self):
        """
        Check whether event succeeded.
        """

        return (
            self.result.upper()
            == "SUCCESS"
        )



    def is_failure(self):
        """
        Check whether event failed.
        """

        return (
            self.result.upper()
            == "FAILED"
        )



    def __repr__(self):
        """
        Developer-friendly representation.
        """

        return (
            f"<SecurityAuditEvent "
            f"{self.event_type}>"
        )
