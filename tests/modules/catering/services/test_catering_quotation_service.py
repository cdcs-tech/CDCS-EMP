"""
Tests for the Catering Quotation application service.
"""

from datetime import date
from decimal import Decimal
from unittest.mock import Mock

import pytest

from app.core.crud.exceptions import (
    EntityNotFoundException,
    EntityValidationException,
)
from app.core.data.sqlalchemy_repository import SQLAlchemyRepository
from app.modules.catering.models import (
    CateringEvent,
    CateringQuotation,
    CateringQuotationLine,
    Customer,
)
from app.modules.catering.repositories import CateringQuotationRepository
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)
from app.modules.catering.services import CateringQuotationService
from app.modules.catering.workflows import CateringQuotationWorkflow


def _make_quotation(
    *,
    status: str = CateringQuotationWorkflow.DRAFT,
    customer_id: int = 1,
    event_id: int = 1,
    lines: list[CateringQuotationLine] | None = None,
) -> CateringQuotation:
    """Create a quotation suitable for isolated service testing."""

    quotation = CateringQuotation(
        customer_id=customer_id,
        event_id=event_id,
        quotation_date=date(2026, 9, 29),
        valid_until=date(2026, 10, 15),
        adjustment_amount=Decimal("0.00"),
        subtotal=Decimal("0.00"),
        total_amount=Decimal("0.00"),
        status=status,
    )

    quotation.lines = lines or []

    return quotation


def _make_line(
    *,
    description: str = "Lunch service",
    quantity: Decimal | str = Decimal("10.000"),
    unit: str = "PERSON",
    unit_price: Decimal | str = Decimal("25.00"),
) -> CateringQuotationLine:
    """Create a quotation line suitable for isolated service testing."""

    return CateringQuotationLine(
        description=description,
        quantity=quantity,
        unit=unit,
        unit_price=unit_price,
        total_amount=Decimal("999999.99"),
    )


def _make_service(
    *,
    repository=None,
    authorization_adapter=None,
    workflow=None,
    customer_repository=None,
    event_repository=None,
):
    """Create a quotation service with isolated dependencies."""

    return CateringQuotationService(
        repository=repository
        or Mock(spec=CateringQuotationRepository),
        authorization_adapter=authorization_adapter,
        workflow=workflow,
        customer_repository=customer_repository
        or Mock(spec=SQLAlchemyRepository),
        event_repository=event_repository
        or Mock(spec=SQLAlchemyRepository),
    )


def _configure_valid_references(
    customer_repository,
    event_repository,
    *,
    customer_id: int = 1,
    event_customer_id: int = 1,
):
    """Configure valid customer and event reference lookups."""

    customer = Mock(
        spec=Customer,
    )
    customer.id = customer_id

    event = Mock(
        spec=CateringEvent,
    )
    event.id = 1
    event.customer_id = event_customer_id

    customer_repository.get_by_id.return_value = customer
    event_repository.get_by_id.return_value = event

    return customer, event


def test_service_uses_default_repository():
    """Verify the service creates its default quotation repository."""

    service = CateringQuotationService()

    assert isinstance(
        service.repository,
        CateringQuotationRepository,
    )


def test_service_accepts_injected_repository():
    """Verify quotation repository dependency injection is preserved."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    service = CateringQuotationService(
        repository=repository,
    )

    assert service.repository is repository


def test_service_accepts_injected_authorization_adapter():
    """Verify authorization adapter dependency injection is preserved."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    service = CateringQuotationService(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    assert service.authorization_adapter is authorization_adapter


def test_service_accepts_injected_workflow():
    """Verify quotation workflow dependency injection is preserved."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    workflow = Mock(
        spec=CateringQuotationWorkflow,
    )

    service = CateringQuotationService(
        repository=repository,
        workflow=workflow,
    )

    assert service.workflow is workflow


def test_service_accepts_injected_reference_repositories():
    """Verify customer and event repository injection is preserved."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    customer_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    event_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    service = CateringQuotationService(
        repository=repository,
        customer_repository=customer_repository,
        event_repository=event_repository,
    )

    assert service.customer_repository is customer_repository
    assert service.event_repository is event_repository


def test_create_requires_authorization_adapter():
    """Verify protected creation fails closed without an adapter."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    quotation = _make_quotation()

    service = _make_service(
        repository=repository,
    )

    with pytest.raises(
        RuntimeError,
        match="Catering authorization adapter is required",
    ):
        service.create(
            quotation,
            subject=Mock(),
        )

    repository.add.assert_not_called()


def test_create_authorizes_before_validation_and_write():
    """Verify CREATE uses the canonical quotation permission."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    customer_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    event_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    _configure_valid_references(
        customer_repository,
        event_repository,
    )

    quotation = _make_quotation()

    repository.add.return_value = quotation

    subject = Mock()

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
        customer_repository=customer_repository,
        event_repository=event_repository,
    )

    result = service.create(
        quotation,
        subject=subject,
    )

    assert result is quotation

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_QUOTATION.CREATE",
    )

    repository.add.assert_called_once_with(
        quotation,
    )


def test_create_denied_does_not_validate_or_write():
    """Verify denied creation cannot reach validation or persistence."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    authorization_adapter.authorize.side_effect = PermissionError(
        "Denied",
    )

    customer_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    event_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    quotation = _make_quotation()

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
        customer_repository=customer_repository,
        event_repository=event_repository,
    )

    with pytest.raises(
        PermissionError,
        match="Denied",
    ):
        service.create(
            quotation,
            subject=Mock(),
        )

    customer_repository.get_by_id.assert_not_called()
    event_repository.get_by_id.assert_not_called()
    repository.add.assert_not_called()


def test_create_rejects_non_draft_quotation():
    """Verify new quotations must begin in DRAFT status."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    quotation = _make_quotation(
        status=CateringQuotationWorkflow.ISSUED,
    )

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    with pytest.raises(
        EntityValidationException,
        match="must be created in DRAFT",
    ):
        service.create(
            quotation,
            subject=Mock(),
        )

    repository.add.assert_not_called()


def test_create_rejects_missing_customer():
    """Verify creation requires an existing customer."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    customer_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    event_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    customer_repository.get_by_id.return_value = None

    quotation = _make_quotation()

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
        customer_repository=customer_repository,
        event_repository=event_repository,
    )

    with pytest.raises(
        EntityValidationException,
        match="customer does not exist",
    ):
        service.create(
            quotation,
            subject=Mock(),
        )

    event_repository.get_by_id.assert_not_called()
    repository.add.assert_not_called()


def test_create_rejects_missing_event():
    """Verify creation requires an existing event."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    customer_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    event_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    customer = Mock(
        spec=Customer,
    )
    customer_repository.get_by_id.return_value = customer
    event_repository.get_by_id.return_value = None

    quotation = _make_quotation()

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
        customer_repository=customer_repository,
        event_repository=event_repository,
    )

    with pytest.raises(
        EntityValidationException,
        match="event does not exist",
    ):
        service.create(
            quotation,
            subject=Mock(),
        )

    repository.add.assert_not_called()


def test_create_rejects_customer_event_mismatch():
    """Verify quotation customer must match event customer."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    customer_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    event_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    _configure_valid_references(
        customer_repository,
        event_repository,
        customer_id=1,
        event_customer_id=2,
    )

    quotation = _make_quotation(
        customer_id=1,
    )

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
        customer_repository=customer_repository,
        event_repository=event_repository,
    )

    with pytest.raises(
        EntityValidationException,
        match="must match the event customer",
    ):
        service.create(
            quotation,
            subject=Mock(),
        )

    repository.add.assert_not_called()


def test_create_rejects_invalid_valid_until_date():
    """Verify quotation validity dates are ordered correctly."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    customer_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    event_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    _configure_valid_references(
        customer_repository,
        event_repository,
    )

    quotation = _make_quotation()
    quotation.valid_until = date(2026, 9, 1)

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
        customer_repository=customer_repository,
        event_repository=event_repository,
    )

    with pytest.raises(
        EntityValidationException,
        match="cannot be earlier",
    ):
        service.create(
            quotation,
            subject=Mock(),
        )

    repository.add.assert_not_called()


def test_create_calculates_line_totals_subtotal_and_total():
    """Verify quotation financial totals are calculated by the service."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    customer_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    event_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    _configure_valid_references(
        customer_repository,
        event_repository,
    )

    lines = [
        _make_line(
            quantity=Decimal("10.000"),
            unit_price=Decimal("25.00"),
        ),
        _make_line(
            description="Drinks",
            quantity=Decimal("5.000"),
            unit_price=Decimal("12.50"),
        ),
    ]

    quotation = _make_quotation(
        lines=lines,
    )
    quotation.adjustment_amount = Decimal("-10.00")

    repository.add.return_value = quotation

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
        customer_repository=customer_repository,
        event_repository=event_repository,
    )

    result = service.create(
        quotation,
        subject=Mock(),
    )

    assert result.subtotal == Decimal("312.50")
    assert result.adjustment_amount == Decimal("-10.00")
    assert result.total_amount == Decimal("302.50")

    assert lines[0].total_amount == Decimal("250.00")
    assert lines[1].total_amount == Decimal("62.50")


def test_create_overwrites_caller_supplied_derived_totals():
    """Verify persisted derived totals are never trusted from callers."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    customer_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    event_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    _configure_valid_references(
        customer_repository,
        event_repository,
    )

    line = _make_line(
        quantity=Decimal("2.000"),
        unit_price=Decimal("15.00"),
    )

    quotation = _make_quotation(
        lines=[line],
    )

    quotation.subtotal = Decimal("9999.99")
    quotation.total_amount = Decimal("8888.88")
    line.total_amount = Decimal("7777.77")

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
        customer_repository=customer_repository,
        event_repository=event_repository,
    )

    service.create(
        quotation,
        subject=Mock(),
    )

    assert line.total_amount == Decimal("30.00")
    assert quotation.subtotal == Decimal("30.00")
    assert quotation.total_amount == Decimal("30.00")


def test_create_rejects_invalid_line_quantity():
    """Verify quotation line quantity must be positive."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    customer_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    event_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    _configure_valid_references(
        customer_repository,
        event_repository,
    )

    quotation = _make_quotation(
        lines=[
            _make_line(
                quantity=Decimal("0.000"),
            ),
        ],
    )

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
        customer_repository=customer_repository,
        event_repository=event_repository,
    )

    with pytest.raises(
        EntityValidationException,
        match="quantity must be greater than zero",
    ):
        service.create(
            quotation,
            subject=Mock(),
        )

    repository.add.assert_not_called()


def test_create_rejects_negative_unit_price():
    """Verify quotation line unit price cannot be negative."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    customer_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    event_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    _configure_valid_references(
        customer_repository,
        event_repository,
    )

    quotation = _make_quotation(
        lines=[
            _make_line(
                unit_price=Decimal("-1.00"),
            ),
        ],
    )

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
        customer_repository=customer_repository,
        event_repository=event_repository,
    )

    with pytest.raises(
        EntityValidationException,
        match="unit price cannot be negative",
    ):
        service.create(
            quotation,
            subject=Mock(),
        )

    repository.add.assert_not_called()


def test_create_rejects_missing_line_description():
    """Verify quotation line description is required."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    customer_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    event_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    _configure_valid_references(
        customer_repository,
        event_repository,
    )

    quotation = _make_quotation(
        lines=[
            _make_line(
                description="",
            ),
        ],
    )

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
        customer_repository=customer_repository,
        event_repository=event_repository,
    )

    with pytest.raises(
        EntityValidationException,
        match="description is required",
    ):
        service.create(
            quotation,
            subject=Mock(),
        )

    repository.add.assert_not_called()


def test_create_rejects_missing_line_unit():
    """Verify quotation line unit is required."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    customer_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    event_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    _configure_valid_references(
        customer_repository,
        event_repository,
    )

    quotation = _make_quotation(
        lines=[
            _make_line(
                unit="",
            ),
        ],
    )

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
        customer_repository=customer_repository,
        event_repository=event_repository,
    )

    with pytest.raises(
        EntityValidationException,
        match="unit is required",
    ):
        service.create(
            quotation,
            subject=Mock(),
        )

    repository.add.assert_not_called()


def test_update_requires_draft_persisted_quotation():
    """Verify only a persisted DRAFT quotation can be updated."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    persisted = _make_quotation(
        status=CateringQuotationWorkflow.ISSUED,
    )

    repository.get_by_id.return_value = persisted

    quotation = _make_quotation(
        status=CateringQuotationWorkflow.DRAFT,
    )
    quotation.id = 1

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    with pytest.raises(
        EntityValidationException,
        match="Only DRAFT quotations",
    ):
        service.update(
            quotation,
            subject=Mock(),
        )

    repository.update.assert_not_called()


def test_update_authorizes_before_persisted_state_check():
    """Verify UPDATE authorization occurs before business validation."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    authorization_adapter.authorize.side_effect = PermissionError(
        "Denied",
    )

    quotation = _make_quotation()
    quotation.id = 1

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    with pytest.raises(
        PermissionError,
        match="Denied",
    ):
        service.update(
            quotation,
            subject=Mock(),
        )

    repository.get_by_id.assert_not_called()
    repository.update.assert_not_called()


def test_update_recalculates_draft_quotation():
    """Verify DRAFT updates recalculate quotation totals."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    customer_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    event_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    _configure_valid_references(
        customer_repository,
        event_repository,
    )

    persisted = _make_quotation()
    persisted.id = 1
    repository.get_by_id.return_value = persisted

    quotation = _make_quotation(
        lines=[
            _make_line(
                quantity=Decimal("4.000"),
                unit_price=Decimal("20.00"),
            ),
        ],
    )
    quotation.id = 1

    repository.update.return_value = quotation

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
        customer_repository=customer_repository,
        event_repository=event_repository,
    )

    result = service.update(
        quotation,
        subject=Mock(),
    )

    assert result is quotation
    assert quotation.subtotal == Decimal("80.00")
    assert quotation.total_amount == Decimal("80.00")

    repository.update.assert_called_once_with(
        quotation,
    )


def test_update_rejects_non_draft_entity_status():
    """Verify an update cannot submit a non-DRAFT entity for editing."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    persisted = _make_quotation()
    persisted.id = 1
    repository.get_by_id.return_value = persisted

    quotation = _make_quotation(
        status=CateringQuotationWorkflow.ISSUED,
    )
    quotation.id = 1

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    with pytest.raises(
        EntityValidationException,
        match="Only DRAFT quotations can be updated",
    ):
        service.update(
            quotation,
            subject=Mock(),
        )

    repository.update.assert_not_called()


def test_delete_rejects_non_draft_quotation():
    """Verify issued quotations cannot be deleted."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    quotation = _make_quotation(
        status=CateringQuotationWorkflow.ISSUED,
    )

    repository.get_by_id.return_value = quotation

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    with pytest.raises(
        EntityValidationException,
        match="Only DRAFT quotations",
    ):
        service.delete(
            1,
            subject=Mock(),
        )

    repository.delete.assert_not_called()


def test_delete_authorizes_before_repository_lookup():
    """Verify DELETE uses the canonical quotation permission."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    quotation = _make_quotation()
    repository.get_by_id.return_value = quotation

    subject = Mock()

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    service.delete(
        1,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_QUOTATION.DELETE",
    )

    repository.get_by_id.assert_called_once_with(
        1,
    )

    repository.delete.assert_called_once_with(
        quotation,
    )


def test_delete_requires_authorization_adapter():
    """Verify protected deletion fails closed."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    service = _make_service(
        repository=repository,
    )

    with pytest.raises(
        RuntimeError,
        match="Catering authorization adapter is required",
    ):
        service.delete(
            1,
            subject=Mock(),
        )

    repository.get_by_id.assert_not_called()
    repository.delete.assert_not_called()


def test_get_delegates_to_repository():
    """Verify inherited quotation retrieval delegates correctly."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    quotation = _make_quotation()
    repository.get_by_id.return_value = quotation

    service = _make_service(
        repository=repository,
    )

    result = service.get(1)

    assert result is quotation

    repository.get_by_id.assert_called_once_with(1)


def test_get_raises_when_quotation_does_not_exist():
    """Verify inherited not-found behaviour."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    repository.get_by_id.return_value = None

    service = _make_service(
        repository=repository,
    )

    with pytest.raises(EntityNotFoundException):
        service.get(999999)

    repository.get_by_id.assert_called_once_with(999999)


def test_issue_requires_authorization_adapter():
    """Verify ISSUE fails closed without an authorization adapter."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    quotation = _make_quotation(
        lines=[
            _make_line(),
        ],
    )

    workflow = Mock(
        spec=CateringQuotationWorkflow,
    )

    service = _make_service(
        repository=repository,
        workflow=workflow,
    )

    with pytest.raises(
        RuntimeError,
        match="Catering authorization adapter is required",
    ):
        service.issue(
            quotation,
            subject=Mock(),
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()


def test_issue_rejects_empty_quotation():
    """Verify a quotation cannot be issued without lines."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    quotation = _make_quotation()

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
    )

    with pytest.raises(
        EntityValidationException,
        match="at least one line",
    ):
        service.issue(
            quotation,
            subject=Mock(),
        )

    repository.update.assert_not_called()


def test_issue_authorizes_validates_transitions_and_persists():
    """Verify ISSUE performs validation, workflow transition and persistence."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    customer_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    event_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    _configure_valid_references(
        customer_repository,
        event_repository,
    )

    quotation = _make_quotation(
        lines=[
            _make_line(
                quantity=Decimal("3.000"),
                unit_price=Decimal("20.00"),
            ),
        ],
    )

    workflow = Mock(
        spec=CateringQuotationWorkflow,
    )

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {
            "name": CateringQuotationWorkflow.ISSUED,
        },
    )()

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
        customer_repository=customer_repository,
        event_repository=event_repository,
    )

    repository.update.return_value = quotation

    result = service.issue(
        quotation,
        subject=Mock(),
    )

    assert result is quotation

    authorization_adapter.authorize.assert_called_once_with(
        authorization_adapter.authorize.call_args.args[0],
        "CATERING.CATERING_QUOTATION.ISSUE",
    )

    workflow.transition.assert_called_once_with(
        CateringQuotationWorkflow.DRAFT,
        CateringQuotationWorkflow.ISSUED,
    )

    assert quotation.status == CateringQuotationWorkflow.ISSUED
    assert quotation.subtotal == Decimal("60.00")
    assert quotation.total_amount == Decimal("60.00")

    repository.update.assert_called_once_with(
        quotation,
    )


def test_issue_denied_does_not_transition_or_persist():
    """Verify denied issuance cannot change state or persist."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    authorization_adapter.authorize.side_effect = PermissionError(
        "Denied",
    )

    workflow = Mock(
        spec=CateringQuotationWorkflow,
    )

    quotation = _make_quotation(
        lines=[
            _make_line(),
        ],
    )

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    with pytest.raises(
        PermissionError,
        match="Denied",
    ):
        service.issue(
            quotation,
            subject=Mock(),
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()
    assert quotation.status == CateringQuotationWorkflow.DRAFT


def test_accept_authorizes_transitions_and_persists():
    """Verify ACCEPT uses its dedicated permission and workflow action."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    quotation = _make_quotation(
        status=CateringQuotationWorkflow.ISSUED,
    )

    workflow = Mock(
        spec=CateringQuotationWorkflow,
    )

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {
            "name": CateringQuotationWorkflow.ACCEPTED,
        },
    )()

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    repository.update.return_value = quotation

    subject = Mock()

    result = service.accept(
        quotation,
        subject=subject,
    )

    assert result is quotation

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_QUOTATION.ACCEPT",
    )

    workflow.transition.assert_called_once_with(
        CateringQuotationWorkflow.ISSUED,
        CateringQuotationWorkflow.ACCEPTED,
    )

    assert quotation.status == CateringQuotationWorkflow.ACCEPTED
    repository.update.assert_called_once_with(quotation)


def test_accept_does_not_coordinate_with_event():
    """
    Verify quotation acceptance does not perform Event confirmation
    coordination in B4.2.
    """

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    event_repository = Mock(
        spec=SQLAlchemyRepository,
    )

    quotation = _make_quotation(
        status=CateringQuotationWorkflow.ISSUED,
    )

    workflow = Mock(
        spec=CateringQuotationWorkflow,
    )

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {
            "name": CateringQuotationWorkflow.ACCEPTED,
        },
    )()

    repository.update.return_value = quotation

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
        event_repository=event_repository,
    )

    result = service.accept(
        quotation,
        subject=Mock(),
    )

    assert result is quotation
    assert quotation.status == CateringQuotationWorkflow.ACCEPTED

    event_repository.get_by_id.assert_not_called()
    repository.update.assert_called_once_with(
        quotation,
    )


def test_accept_denied_does_not_transition_or_persist():
    """Verify denied acceptance cannot mutate quotation state."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    authorization_adapter.authorize.side_effect = PermissionError(
        "Denied",
    )

    workflow = Mock(
        spec=CateringQuotationWorkflow,
    )

    quotation = _make_quotation(
        status=CateringQuotationWorkflow.ISSUED,
    )

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    with pytest.raises(
        PermissionError,
        match="Denied",
    ):
        service.accept(
            quotation,
            subject=Mock(),
        )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()
    assert quotation.status == CateringQuotationWorkflow.ISSUED


def test_decline_authorizes_transitions_and_persists():
    """Verify DECLINE uses its dedicated permission."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    quotation = _make_quotation(
        status=CateringQuotationWorkflow.ISSUED,
    )

    workflow = Mock(
        spec=CateringQuotationWorkflow,
    )

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {
            "name": CateringQuotationWorkflow.DECLINED,
        },
    )()

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    subject = Mock()

    service.decline(
        quotation,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_QUOTATION.DECLINE",
    )

    workflow.transition.assert_called_once_with(
        CateringQuotationWorkflow.ISSUED,
        CateringQuotationWorkflow.DECLINED,
    )

    assert quotation.status == CateringQuotationWorkflow.DECLINED
    repository.update.assert_called_once_with(quotation)


def test_expire_authorizes_transitions_and_persists():
    """Verify EXPIRE uses its dedicated permission."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    quotation = _make_quotation(
        status=CateringQuotationWorkflow.ISSUED,
    )

    workflow = Mock(
        spec=CateringQuotationWorkflow,
    )

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {
            "name": CateringQuotationWorkflow.EXPIRED,
        },
    )()

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    subject = Mock()

    service.expire(
        quotation,
        subject=subject,
    )

    authorization_adapter.authorize.assert_called_once_with(
        subject,
        "CATERING.CATERING_QUOTATION.EXPIRE",
    )

    workflow.transition.assert_called_once_with(
        CateringQuotationWorkflow.ISSUED,
        CateringQuotationWorkflow.EXPIRED,
    )

    assert quotation.status == CateringQuotationWorkflow.EXPIRED
    repository.update.assert_called_once_with(quotation)


def test_expire_does_not_automatically_depend_on_valid_until_date():
    """
    Verify explicit expiry remains an action rather than an automatic
    date-driven transition.
    """

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    authorization_adapter = Mock(
        spec=CateringAuthorizationAdapter,
    )

    quotation = _make_quotation(
        status=CateringQuotationWorkflow.ISSUED,
    )
    quotation.valid_until = date(2030, 1, 1)

    workflow = Mock(
        spec=CateringQuotationWorkflow,
    )

    workflow.transition.return_value = type(
        "WorkflowState",
        (),
        {
            "name": CateringQuotationWorkflow.EXPIRED,
        },
    )()

    service = _make_service(
        repository=repository,
        authorization_adapter=authorization_adapter,
        workflow=workflow,
    )

    service.expire(
        quotation,
        subject=Mock(),
    )

    assert quotation.status == CateringQuotationWorkflow.EXPIRED
    workflow.transition.assert_called_once_with(
        CateringQuotationWorkflow.ISSUED,
        CateringQuotationWorkflow.EXPIRED,
    )


def test_lifecycle_action_requires_authorization_adapter():
    """Verify lifecycle operations fail closed without authorization."""

    repository = Mock(
        spec=CateringQuotationRepository,
    )

    workflow = Mock(
        spec=CateringQuotationWorkflow,
    )

    quotation = _make_quotation(
        status=CateringQuotationWorkflow.ISSUED,
    )

    service = _make_service(
        repository=repository,
        workflow=workflow,
    )

    for operation in (
        service.accept,
        service.decline,
        service.expire,
    ):
        with pytest.raises(
            RuntimeError,
            match="Catering authorization adapter is required",
        ):
            operation(
                quotation,
                subject=Mock(),
            )

    workflow.transition.assert_not_called()
    repository.update.assert_not_called()
