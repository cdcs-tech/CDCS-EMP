"""
Tests for the Catering -> Procurement handoff coordinator.
"""

from unittest.mock import Mock

import pytest

from app.core.crud.exceptions import EntityNotFoundException
from app.modules.catering.models import (
    CateringEvent,
    CateringPurchaseRequirement,
    EventRequirement,
)
from app.modules.catering.repositories import (
    CateringEventRepository,
    CateringPurchaseRequirementRepository,
    EventRequirementRepository,
)
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)
from app.modules.catering.services import (
    CateringProcurementHandoffService,
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


def _catering_purchase_requirement(
    *,
    event_requirement_id=10,
    guid="CPR-GUID-001",
    procurement_reference=None,
):
    requirement = Mock(
        spec=CateringPurchaseRequirement,
    )
    requirement.id = 1
    requirement.guid = guid
    requirement.event_requirement_id = event_requirement_id
    requirement.description = "Catering food supplies"
    requirement.required_by_date = None
    requirement.procurement_reference = procurement_reference
    return requirement


def _event_requirement(
    *,
    event_id=20,
    fulfilment_type="PROCUREMENT",
):
    requirement = Mock(
        spec=EventRequirement,
    )
    requirement.id = 10
    requirement.event_id = event_id
    requirement.fulfilment_type = fulfilment_type
    return requirement


def _confirmed_event():
    event = Mock(
        spec=CateringEvent,
    )
    event.status = CateringEventWorkflow.CONFIRMED
    return event


def _service(
    purchase_requirement_repository=None,
    event_requirement_repository=None,
    event_repository=None,
    procurement_repository=None,
    authorization_adapter=None,
):
    return CateringProcurementHandoffService(
        purchase_requirement_repository=(
            purchase_requirement_repository
            or Mock(
                spec=CateringPurchaseRequirementRepository,
            )
        ),
        event_requirement_repository=(
            event_requirement_repository
            or Mock(
                spec=EventRequirementRepository,
            )
        ),
        event_repository=(
            event_repository
            or Mock(
                spec=CateringEventRepository,
            )
        ),
        procurement_repository=(
            procurement_repository
            or Mock(
                spec=PurchaseRequirementRepository,
            )
        ),
        authorization_adapter=(
            authorization_adapter
            or Mock(
                spec=CateringAuthorizationAdapter,
            )
        ),
    )


def _configure_valid_handoff(
    purchase_requirement_repository,
    event_requirement_repository,
    event_repository,
    procurement_repository,
):
    source = _catering_purchase_requirement()
    event_requirement = _event_requirement()
    event = _confirmed_event()

    purchase_requirement_repository.get_by_id.return_value = source
    event_requirement_repository.get_by_id.return_value = (
        event_requirement
    )
    event_repository.get_by_id.return_value = event
    procurement_repository.get_by_reference.return_value = None

    return source, event_requirement, event


def test_service_uses_default_dependencies():
    service = CateringProcurementHandoffService(
        authorization_adapter=Mock(
            spec=CateringAuthorizationAdapter,
        ),
    )

    assert isinstance(
        service.purchase_requirement_repository,
        CateringPurchaseRequirementRepository,
    )
    assert isinstance(
        service.event_requirement_repository,
        EventRequirementRepository,
    )
    assert isinstance(
        service.event_repository,
        CateringEventRepository,
    )
    assert isinstance(
        service.procurement_repository,
        PurchaseRequirementRepository,
    )


def test_submit_requires_authorization_adapter():
    service = CateringProcurementHandoffService()

    with pytest.raises(
        RuntimeError,
        match="Catering authorization adapter is required",
    ):
        service.submit_to_procurement(
            _catering_purchase_requirement(),
            subject=Mock(),
        )


def test_submit_authorizes_before_source_validation():
    purchase_requirement_repository = Mock(
        spec=CateringPurchaseRequirementRepository,
    )
    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )
    authorization_adapter.authorize.side_effect = PermissionError(
        "Denied",
    )

    service = _service(
        purchase_requirement_repository=(
            purchase_requirement_repository
        ),
        authorization_adapter=authorization_adapter,
    )

    with pytest.raises(
        PermissionError,
        match="Denied",
    ):
        service.submit_to_procurement(
            _catering_purchase_requirement(),
            subject=Mock(),
        )

    purchase_requirement_repository.get_by_id.assert_not_called()


def test_submit_rejects_missing_catering_purchase_requirement():
    purchase_requirement_repository = Mock(
        spec=CateringPurchaseRequirementRepository,
    )
    purchase_requirement_repository.get_by_id.return_value = None

    service = _service(
        purchase_requirement_repository=(
            purchase_requirement_repository
        ),
    )

    with pytest.raises(
        EntityNotFoundException,
        match="CateringPurchaseRequirement",
    ):
        service.submit_to_procurement(
            _catering_purchase_requirement(),
            subject=Mock(),
        )


def test_submit_rejects_missing_event_requirement():
    purchase_requirement_repository = Mock(
        spec=CateringPurchaseRequirementRepository,
    )
    event_requirement_repository = Mock(
        spec=EventRequirementRepository,
    )

    source = _catering_purchase_requirement()

    purchase_requirement_repository.get_by_id.return_value = source
    event_requirement_repository.get_by_id.return_value = None

    service = _service(
        purchase_requirement_repository=(
            purchase_requirement_repository
        ),
        event_requirement_repository=event_requirement_repository,
    )

    with pytest.raises(
        EntityNotFoundException,
        match="EventRequirement",
    ):
        service.submit_to_procurement(
            source,
            subject=Mock(),
        )


def test_submit_rejects_non_procurement_fulfilment():
    purchase_requirement_repository = Mock(
        spec=CateringPurchaseRequirementRepository,
    )
    event_requirement_repository = Mock(
        spec=EventRequirementRepository,
    )

    source = _catering_purchase_requirement()
    event_requirement = _event_requirement(
        fulfilment_type="INVENTORY",
    )

    purchase_requirement_repository.get_by_id.return_value = source
    event_requirement_repository.get_by_id.return_value = (
        event_requirement
    )

    service = _service(
        purchase_requirement_repository=(
            purchase_requirement_repository
        ),
        event_requirement_repository=event_requirement_repository,
    )

    with pytest.raises(
        ValueError,
        match="Only PROCUREMENT Event Requirements",
    ):
        service.submit_to_procurement(
            source,
            subject=Mock(),
        )


def test_submit_rejects_unconfirmed_event():
    purchase_requirement_repository = Mock(
        spec=CateringPurchaseRequirementRepository,
    )
    event_requirement_repository = Mock(
        spec=EventRequirementRepository,
    )
    event_repository = Mock(
        spec=CateringEventRepository,
    )

    source = _catering_purchase_requirement()
    event_requirement = _event_requirement()

    event = Mock(
        spec=CateringEvent,
    )
    event.status = CateringEventWorkflow.PLANNING

    purchase_requirement_repository.get_by_id.return_value = source
    event_requirement_repository.get_by_id.return_value = (
        event_requirement
    )
    event_repository.get_by_id.return_value = event

    service = _service(
        purchase_requirement_repository=(
            purchase_requirement_repository
        ),
        event_requirement_repository=event_requirement_repository,
        event_repository=event_repository,
    )

    with pytest.raises(
        ValueError,
        match="CONFIRMED Catering Event",
    ):
        service.submit_to_procurement(
            source,
            subject=Mock(),
        )


def test_submit_creates_procurement_requirement_and_links_source():
    purchase_requirement_repository = Mock(
        spec=CateringPurchaseRequirementRepository,
    )
    event_requirement_repository = Mock(
        spec=EventRequirementRepository,
    )
    event_repository = Mock(
        spec=CateringEventRepository,
    )
    procurement_repository = Mock(
        spec=PurchaseRequirementRepository,
    )
    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    source, event_requirement, event = _configure_valid_handoff(
        purchase_requirement_repository,
        event_requirement_repository,
        event_repository,
        procurement_repository,
    )

    created = PurchaseRequirement(
        reference="CATERING-PR-CPR-GUID-001",
        description=source.description,
        source_module="CATERING",
        source_type="CATERING_PURCHASE_REQUIREMENT",
        source_reference="CPR-GUID-001",
        required_by_date=source.required_by_date,
    )

    procurement_repository.add.return_value = created

    service = _service(
        purchase_requirement_repository=(
            purchase_requirement_repository
        ),
        event_requirement_repository=event_requirement_repository,
        event_repository=event_repository,
        procurement_repository=procurement_repository,
        authorization_adapter=authorization_adapter,
    )

    subject = Mock()

    result = service.submit_to_procurement(
        source,
        subject=subject,
    )

    assert result is created

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_PURCHASE_REQUIREMENT.SUBMIT_TO_PROCUREMENT",
    )

    procurement_repository.get_by_reference.assert_called_once_with(
        "CATERING-PR-CPR-GUID-001",
    )
    procurement_repository.add.assert_called_once()

    created_requirement = (
        procurement_repository.add.call_args.args[0]
    )

    assert created_requirement.reference == (
        "CATERING-PR-CPR-GUID-001"
    )
    assert created_requirement.description == (
        "Catering food supplies"
    )
    assert created_requirement.source_module == "CATERING"
    assert created_requirement.source_type == (
        "CATERING_PURCHASE_REQUIREMENT"
    )
    assert created_requirement.source_reference == (
        "CPR-GUID-001"
    )

    assert source.procurement_reference == (
        "CATERING-PR-CPR-GUID-001"
    )
    purchase_requirement_repository.update.assert_called_once_with(
        source,
    )


def test_submit_reuses_matching_existing_procurement_requirement():
    purchase_requirement_repository = Mock(
        spec=CateringPurchaseRequirementRepository,
    )
    event_requirement_repository = Mock(
        spec=EventRequirementRepository,
    )
    event_repository = Mock(
        spec=CateringEventRepository,
    )
    procurement_repository = Mock(
        spec=PurchaseRequirementRepository,
    )

    source, _, _ = _configure_valid_handoff(
        purchase_requirement_repository,
        event_requirement_repository,
        event_repository,
        procurement_repository,
    )

    existing = Mock(
        spec=PurchaseRequirement,
    )
    existing.reference = "CATERING-PR-CPR-GUID-001"
    existing.source_module = "CATERING"
    existing.source_type = "CATERING_PURCHASE_REQUIREMENT"
    existing.source_reference = "CPR-GUID-001"

    procurement_repository.get_by_reference.return_value = (
        existing
    )

    service = _service(
        purchase_requirement_repository=(
            purchase_requirement_repository
        ),
        event_requirement_repository=event_requirement_repository,
        event_repository=event_repository,
        procurement_repository=procurement_repository,
    )

    result = service.submit_to_procurement(
        source,
        subject=Mock(),
    )

    assert result is existing
    procurement_repository.add.assert_not_called()

    assert source.procurement_reference == (
        "CATERING-PR-CPR-GUID-001"
    )
    purchase_requirement_repository.update.assert_called_once_with(
        source,
    )


@pytest.mark.parametrize(
    "field, value",
    [
        (
            "source_module",
            "OTHER_MODULE",
        ),
        (
            "source_type",
            "OTHER_TYPE",
        ),
        (
            "source_reference",
            "OTHER-CPR",
        ),
    ],
)
def test_submit_rejects_conflicting_existing_procurement_record(
    field,
    value,
):
    purchase_requirement_repository = Mock(
        spec=CateringPurchaseRequirementRepository,
    )
    event_requirement_repository = Mock(
        spec=EventRequirementRepository,
    )
    event_repository = Mock(
        spec=CateringEventRepository,
    )
    procurement_repository = Mock(
        spec=PurchaseRequirementRepository,
    )

    source, _, _ = _configure_valid_handoff(
        purchase_requirement_repository,
        event_requirement_repository,
        event_repository,
        procurement_repository,
    )

    existing = Mock(
        spec=PurchaseRequirement,
    )
    existing.reference = "CATERING-PR-CPR-GUID-001"
    existing.source_module = "CATERING"
    existing.source_type = "CATERING_PURCHASE_REQUIREMENT"
    existing.source_reference = "CPR-GUID-001"

    setattr(
        existing,
        field,
        value,
    )

    procurement_repository.get_by_reference.return_value = (
        existing
    )

    service = _service(
        purchase_requirement_repository=(
            purchase_requirement_repository
        ),
        event_requirement_repository=event_requirement_repository,
        event_repository=event_repository,
        procurement_repository=procurement_repository,
    )

    with pytest.raises(
        ValueError,
        match="conflicting",
    ):
        service.submit_to_procurement(
            source,
            subject=Mock(),
        )

    procurement_repository.add.assert_not_called()
    purchase_requirement_repository.update.assert_not_called()


def test_submit_rejects_existing_different_procurement_reference():
    purchase_requirement_repository = Mock(
        spec=CateringPurchaseRequirementRepository,
    )
    event_requirement_repository = Mock(
        spec=EventRequirementRepository,
    )
    event_repository = Mock(
        spec=CateringEventRepository,
    )

    source, _, _ = _configure_valid_handoff(
        purchase_requirement_repository,
        event_requirement_repository,
        event_repository,
        Mock(
            spec=PurchaseRequirementRepository,
        ),
    )
    source.procurement_reference = "OTHER-REFERENCE"

    service = _service(
        purchase_requirement_repository=(
            purchase_requirement_repository
        ),
        event_requirement_repository=event_requirement_repository,
        event_repository=event_repository,
    )

    with pytest.raises(
        ValueError,
        match="different Procurement requirement",
    ):
        service.submit_to_procurement(
            source,
            subject=Mock(),
        )


def test_submit_does_not_create_downstream_procurement_lifecycle_records():
    purchase_requirement_repository = Mock(
        spec=CateringPurchaseRequirementRepository,
    )
    event_requirement_repository = Mock(
        spec=EventRequirementRepository,
    )
    event_repository = Mock(
        spec=CateringEventRepository,
    )
    procurement_repository = Mock(
        spec=PurchaseRequirementRepository,
    )

    source, _, _ = _configure_valid_handoff(
        purchase_requirement_repository,
        event_requirement_repository,
        event_repository,
        procurement_repository,
    )

    created = PurchaseRequirement(
        reference="CATERING-PR-CPR-GUID-001",
        description=source.description,
        source_module="CATERING",
        source_type="CATERING_PURCHASE_REQUIREMENT",
        source_reference="CPR-GUID-001",
    )
    procurement_repository.add.return_value = created

    service = _service(
        purchase_requirement_repository=(
            purchase_requirement_repository
        ),
        event_requirement_repository=event_requirement_repository,
        event_repository=event_repository,
        procurement_repository=procurement_repository,
    )

    service.submit_to_procurement(
        source,
        subject=Mock(),
    )

    assert procurement_repository.method_calls
    assert (
        procurement_repository.method_calls[0].args
        == ("CATERING-PR-CPR-GUID-001",)
    )


def test_submit_uses_only_handoff_permission():
    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    purchase_requirement_repository = Mock(
        spec=CateringPurchaseRequirementRepository,
    )
    event_requirement_repository = Mock(
        spec=EventRequirementRepository,
    )
    event_repository = Mock(
        spec=CateringEventRepository,
    )
    procurement_repository = Mock(
        spec=PurchaseRequirementRepository,
    )

    source, _, _ = _configure_valid_handoff(
        purchase_requirement_repository,
        event_requirement_repository,
        event_repository,
        procurement_repository,
    )

    created = PurchaseRequirement(
        reference="CATERING-PR-CPR-GUID-001",
        description=source.description,
        source_module="CATERING",
        source_type="CATERING_PURCHASE_REQUIREMENT",
        source_reference="CPR-GUID-001",
    )
    procurement_repository.add.return_value = created

    subject = Mock()

    service = _service(
        purchase_requirement_repository=(
            purchase_requirement_repository
        ),
        event_requirement_repository=event_requirement_repository,
        event_repository=event_repository,
        procurement_repository=procurement_repository,
        authorization_adapter=authorization_adapter,
    )

    service.submit_to_procurement(
        source,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_PURCHASE_REQUIREMENT.SUBMIT_TO_PROCUREMENT",
    )
