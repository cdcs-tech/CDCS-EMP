"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Services

Catering Purchase Requirement -> Procurement handoff coordinator.
"""

from app.core.crud.exceptions import (
    EntityNotFoundException,
)

from app.modules.catering.models import (
    CateringPurchaseRequirement,
)
from app.modules.catering.repositories import (
    CateringEventRepository,
    CateringPurchaseRequirementRepository,
    EventRequirementRepository,
)
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)
from app.modules.catering.workflows import (
    CateringEventWorkflow,
)
from app.modules.procurement.models import (
    PurchaseRequirement,
)
from app.modules.procurement.repositories import (
    PurchaseRequirementRepository,
)


class CateringProcurementHandoffService:
    """
    Coordinate the same-database Catering -> Procurement handoff.

    This service owns the application boundary for registering a
    Catering Purchase Requirement as an existing Procurement
    PurchaseRequirement.

    It does not own Procurement lifecycle operations and does not
    commit or roll back transactions.
    """

    SUBMIT_PERMISSION = (
        "CATERING.CATERING_PURCHASE_REQUIREMENT.SUBMIT_TO_PROCUREMENT"
    )

    SOURCE_MODULE = "CATERING"
    SOURCE_TYPE = "CATERING_PURCHASE_REQUIREMENT"
    REFERENCE_PREFIX = "CATERING-PR-"

    def __init__(
        self,
        *,
        purchase_requirement_repository=None,
        event_requirement_repository=None,
        event_repository=None,
        procurement_repository=None,
        authorization_adapter=None,
    ) -> None:
        """
        Initialize the handoff coordinator.

        Dependencies remain injectable so the coordinator can be
        tested without coupling tests to concrete persistence.
        """

        self.purchase_requirement_repository = (
            purchase_requirement_repository
            or CateringPurchaseRequirementRepository()
        )

        self.event_requirement_repository = (
            event_requirement_repository
            or EventRequirementRepository()
        )

        self.event_repository = (
            event_repository
            or CateringEventRepository()
        )

        self.procurement_repository = (
            procurement_repository
            or PurchaseRequirementRepository()
        )

        self.authorization_adapter = authorization_adapter

    def _authorize(
        self,
        subject,
    ) -> None:
        """
        Authorize the Catering handoff operation.

        The handoff fails closed when the Catering authorization
        adapter has not been supplied.
        """

        if self.authorization_adapter is None:
            raise RuntimeError(
                "Catering authorization adapter is required",
            )

        self.authorization_adapter.authorize(
            subject,
            self.SUBMIT_PERMISSION,
        )

    def _get_source_requirement(
        self,
        purchase_requirement: CateringPurchaseRequirement,
    ) -> CateringPurchaseRequirement:
        """
        Load the authoritative Catering Purchase Requirement.
        """

        requirement_id = getattr(
            purchase_requirement,
            "id",
            None,
        )

        if requirement_id is None:
            raise EntityNotFoundException(
                "CateringPurchaseRequirement",
                requirement_id,
            )

        source = self.purchase_requirement_repository.get_by_id(
            requirement_id,
        )

        if source is None:
            raise EntityNotFoundException(
                "CateringPurchaseRequirement",
                requirement_id,
            )

        return source

    def _get_event_requirement(
        self,
        purchase_requirement: CateringPurchaseRequirement,
    ):
        """
        Load the originating Catering Event Requirement.
        """

        event_requirement = (
            self.event_requirement_repository.get_by_id(
                purchase_requirement.event_requirement_id,
            )
        )

        if event_requirement is None:
            raise EntityNotFoundException(
                "EventRequirement",
                purchase_requirement.event_requirement_id,
            )

        return event_requirement

    def _get_confirmed_event(
        self,
        event_requirement,
    ):
        """
        Load and validate the originating confirmed Catering Event.
        """

        event = self.event_repository.get_by_id(
            event_requirement.event_id,
        )

        if event is None:
            raise EntityNotFoundException(
                "CateringEvent",
                event_requirement.event_id,
            )

        if event.status != CateringEventWorkflow.CONFIRMED:
            raise ValueError(
                "Catering Purchase Requirement handoff requires "
                "a CONFIRMED Catering Event",
            )

        return event

    @classmethod
    def _reference_for(
        cls,
        purchase_requirement: CateringPurchaseRequirement,
    ) -> str:
        """
        Build the deterministic Procurement reference.
        """

        return (
            f"{cls.REFERENCE_PREFIX}"
            f"{purchase_requirement.guid}"
        )

    @staticmethod
    def _source_reference(
        purchase_requirement: CateringPurchaseRequirement,
    ) -> str:
        """
        Return the immutable Catering Purchase Requirement identity
        used as Procurement source_reference.
        """

        return str(
            purchase_requirement.guid,
        )

    @classmethod
    def _validate_existing_procurement_record(
        cls,
        procurement_requirement: PurchaseRequirement,
        *,
        source_reference: str,
    ) -> None:
        """
        Validate that an existing Procurement record belongs to
        this Catering Purchase Requirement.
        """

        if (
            procurement_requirement.source_module
            != cls.SOURCE_MODULE
        ):
            raise ValueError(
                "Procurement reference collision has conflicting "
                "source_module metadata",
            )

        if (
            procurement_requirement.source_type
            != cls.SOURCE_TYPE
        ):
            raise ValueError(
                "Procurement reference collision has conflicting "
                "source_type metadata",
            )

        if (
            procurement_requirement.source_reference
            != source_reference
        ):
            raise ValueError(
                "Procurement reference collision has conflicting "
                "source_reference metadata",
            )

    def submit_to_procurement(
        self,
        purchase_requirement: CateringPurchaseRequirement,
        *,
        subject,
    ) -> PurchaseRequirement:
        """
        Register a Catering Purchase Requirement with Procurement.

        The operation is idempotent through the deterministic
        Procurement reference derived from the immutable Catering
        Purchase Requirement GUID.

        The surrounding enterprise transaction owns commit/rollback.
        """

        self._authorize(
            subject,
        )

        source = self._get_source_requirement(
            purchase_requirement,
        )

        event_requirement = self._get_event_requirement(
            source,
        )

        if event_requirement.fulfilment_type != "PROCUREMENT":
            raise ValueError(
                "Only PROCUREMENT Event Requirements can be "
                "submitted to Procurement",
            )

        self._get_confirmed_event(
            event_requirement,
        )

        reference = self._reference_for(
            source,
        )

        source_reference = self._source_reference(
            source,
        )

        if (
            source.procurement_reference is not None
            and source.procurement_reference != reference
        ):
            raise ValueError(
                "Catering Purchase Requirement already references "
                "a different Procurement requirement",
            )

        existing = self.procurement_repository.get_by_reference(
            reference,
        )

        if existing is not None:
            self._validate_existing_procurement_record(
                existing,
                source_reference=source_reference,
            )

            if source.procurement_reference != reference:
                source.procurement_reference = reference

                self.purchase_requirement_repository.update(
                    source,
                )

            return existing

        procurement_requirement = PurchaseRequirement(
            reference=reference,
            description=source.description,
            source_module=self.SOURCE_MODULE,
            source_type=self.SOURCE_TYPE,
            source_reference=source_reference,
            required_by_date=source.required_by_date,
        )

        procurement_requirement = (
            self.procurement_repository.add(
                procurement_requirement,
            )
        )

        source.procurement_reference = (
            procurement_requirement.reference
        )

        self.purchase_requirement_repository.update(
            source,
        )

        return procurement_requirement


__all__ = [
    "CateringProcurementHandoffService",
]
