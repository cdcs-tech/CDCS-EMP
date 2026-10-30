from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch
from uuid import uuid4

import pytest

from app.core.crud.exceptions import EntityValidationException
from app.modules.catering.services.procurement_delivery_evidence import (
    ProcurementDeliveryEvidenceResolver,
)
from app.modules.procurement.integration import (
    INVENTORY_INTEGRATION_PROVIDER,
    INVENTORY_QUERY_PURCHASE_ORDER_LINE_RECEIPT_STATUS_OPERATION,
    InventoryReceiptStatusQueryResult,
)


def _scalar_result(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


def _scalars_result(values):
    result = MagicMock()
    result.scalars.return_value.all.return_value = values
    return result


def _valid_graph():
    line_guid = uuid4()
    event_requirement = SimpleNamespace(
        id=11,
        item_reference="RICE-CDCS-TOT-001",
        unit="kg",
        stock_item_id=5,
    )
    catering_requirement = SimpleNamespace(
        procurement_reference="CATERING-PR-TEST",
    )
    procurement_requirement = SimpleNamespace(id=7)
    purchase_request_line = SimpleNamespace(
        is_deleted=False,
        item_reference="RICE-CDCS-TOT-001",
        unit="kg",
    )
    purchase_request = SimpleNamespace(
        id=8,
        status="APPROVED",
        lines=[purchase_request_line],
    )
    purchase_order_line = SimpleNamespace(
        is_deleted=False,
        item_reference="RICE-CDCS-TOT-001",
        stock_item_reference="TOT-RICE-001",
        unit="kg",
        guid=line_guid,
    )
    purchase_order = SimpleNamespace(
        id=9,
        status="APPROVED",
        reference="PO-CDCS-TOT-TEST-001",
        lines=[purchase_order_line],
    )
    product = SimpleNamespace(
        code="TOT-RICE-001",
        is_deleted=False,
    )
    stock_item = SimpleNamespace(
        is_deleted=False,
        product=product,
    )

    return SimpleNamespace(
        event_requirement=event_requirement,
        catering_requirement=catering_requirement,
        procurement_requirement=procurement_requirement,
        purchase_request=purchase_request,
        purchase_order=purchase_order,
        purchase_order_line=purchase_order_line,
        stock_item=stock_item,
        line_guid=line_guid,
    )


def _configure_valid_database(mock_db, graph):
    execute_results = [
        _scalar_result(graph.catering_requirement),
        _scalar_result(graph.procurement_requirement),
        _scalars_result([graph.purchase_request]),
        _scalars_result([graph.purchase_order]),
    ]
    mock_db.session.execute.side_effect = execute_results
    mock_db.session.get.return_value = graph.stock_item


def _successful_integration_result(graph):
    receipt_status_data = {
        "success": True,
        "purchase_order_reference": graph.purchase_order.reference,
        "purchase_order_line_reference": f"PO-LINE-{graph.line_guid}",
        "received_quantity": 30,
        "unit": "kg",
        "receipt_count": 1,
        "has_receipts": True,
        "error_code": None,
    }
    response = SimpleNamespace(data=receipt_status_data)

    expected_receipt_status = InventoryReceiptStatusQueryResult(
        **receipt_status_data,
    )

    return (
        SimpleNamespace(success=True, response=response),
        expected_receipt_status,
    )


def test_resolver_queries_exact_approved_po_line_receipt_status():
    graph = _valid_graph()
    integration_result, receipt_status = _successful_integration_result(graph)

    with (
        patch(
            "app.modules.catering.services.procurement_delivery_evidence.db"
        ) as mock_db,
        patch(
            "app.modules.catering.services.procurement_delivery_evidence.integration_service"
        ) as mock_integration,
    ):
        _configure_valid_database(mock_db, graph)
        mock_integration.execute.return_value = integration_result

        result = ProcurementDeliveryEvidenceResolver().get_receipt_status(
            graph.event_requirement
        )

    assert result == receipt_status
    mock_integration.execute.assert_called_once()

    request = mock_integration.execute.call_args.args[0]
    assert request.provider == INVENTORY_INTEGRATION_PROVIDER
    assert (
        request.operation
        == INVENTORY_QUERY_PURCHASE_ORDER_LINE_RECEIPT_STATUS_OPERATION
    )
    assert request.payload.purchase_order_reference == (
        "PO-CDCS-TOT-TEST-001"
    )
    assert request.payload.purchase_order_line_reference == (
        f"PO-LINE-{graph.line_guid}"
    )
    assert request.payload.stock_item_reference == "TOT-RICE-001"


def test_resolver_rejects_unpersisted_event_requirement():
    with pytest.raises(
        EntityValidationException,
        match="not persisted",
    ):
        ProcurementDeliveryEvidenceResolver().get_receipt_status(
            SimpleNamespace(id=None)
        )


def test_resolver_rejects_missing_catering_purchase_requirement():
    with patch(
        "app.modules.catering.services.procurement_delivery_evidence.db"
    ) as mock_db:
        mock_db.session.execute.return_value = _scalar_result(None)

        with pytest.raises(
            EntityValidationException,
            match="no linked Catering Purchase Requirement",
        ):
            ProcurementDeliveryEvidenceResolver().get_receipt_status(
                SimpleNamespace(id=11)
            )


def test_resolver_rejects_when_no_approved_purchase_request_exists():
    graph = _valid_graph()
    graph.purchase_request.status = "DRAFT"

    with patch(
        "app.modules.catering.services.procurement_delivery_evidence.db"
    ) as mock_db:
        mock_db.session.execute.side_effect = [
            _scalar_result(graph.catering_requirement),
            _scalar_result(graph.procurement_requirement),
            _scalars_result([graph.purchase_request]),
        ]

        with pytest.raises(
            EntityValidationException,
            match="APPROVED Purchase Request",
        ):
            ProcurementDeliveryEvidenceResolver().get_receipt_status(
                graph.event_requirement
            )


def test_resolver_rejects_ambiguous_purchase_request_lines():
    graph = _valid_graph()
    duplicate_line = SimpleNamespace(
        is_deleted=False,
        item_reference="RICE-CDCS-TOT-001",
        unit="kg",
    )
    graph.purchase_request.lines.append(duplicate_line)

    with patch(
        "app.modules.catering.services.procurement_delivery_evidence.db"
    ) as mock_db:
        mock_db.session.execute.side_effect = [
            _scalar_result(graph.catering_requirement),
            _scalar_result(graph.procurement_requirement),
            _scalars_result([graph.purchase_request]),
        ]
        mock_db.session.get.return_value = graph.stock_item

        with pytest.raises(
            EntityValidationException,
            match="ambiguous matching lines",
        ):
            ProcurementDeliveryEvidenceResolver().get_receipt_status(
                graph.event_requirement
            )


def test_resolver_rejects_ambiguous_approved_purchase_order_lines():
    graph = _valid_graph()
    duplicate_line = SimpleNamespace(
        is_deleted=False,
        item_reference="RICE-CDCS-TOT-001",
        stock_item_reference="TOT-RICE-001",
        unit="kg",
        guid=uuid4(),
    )
    graph.purchase_order.lines.append(duplicate_line)

    with patch(
        "app.modules.catering.services.procurement_delivery_evidence.db"
    ) as mock_db:
        _configure_valid_database(mock_db, graph)

        with pytest.raises(
            EntityValidationException,
            match="ambiguous matching lines",
        ):
            ProcurementDeliveryEvidenceResolver().get_receipt_status(
                graph.event_requirement
            )


def test_resolver_rejects_when_no_consistent_approved_po_line_exists():
    graph = _valid_graph()
    graph.purchase_order_line.stock_item_reference = "UNRELATED-STOCK-CODE"

    with (
        patch(
            "app.modules.catering.services.procurement_delivery_evidence.db"
        ) as mock_db,
        patch(
            "app.modules.catering.services.procurement_delivery_evidence.integration_service"
        ) as mock_integration,
    ):
        _configure_valid_database(mock_db, graph)

        with pytest.raises(
            EntityValidationException,
            match="exactly one consistent approved Purchase Order line",
        ):
            ProcurementDeliveryEvidenceResolver().get_receipt_status(
                graph.event_requirement
            )

    mock_integration.execute.assert_not_called()


def test_resolver_rejects_when_integration_query_is_unsuccessful():
    graph = _valid_graph()

    with (
        patch(
            "app.modules.catering.services.procurement_delivery_evidence.db"
        ) as mock_db,
        patch(
            "app.modules.catering.services.procurement_delivery_evidence.integration_service"
        ) as mock_integration,
    ):
        _configure_valid_database(mock_db, graph)
        mock_integration.execute.return_value = SimpleNamespace(
            success=False,
            response=None,
        )

        with pytest.raises(
            EntityValidationException,
            match="query is unavailable",
        ):
            ProcurementDeliveryEvidenceResolver().get_receipt_status(
                graph.event_requirement
            )


def test_resolver_rejects_receipt_response_for_a_different_po_line():
    graph = _valid_graph()
    integration_result, _ = _successful_integration_result(graph)
    integration_result.response.data[
        "purchase_order_line_reference"
    ] = "PO-LINE-UNRELATED"

    with (
        patch(
            "app.modules.catering.services.procurement_delivery_evidence.db"
        ) as mock_db,
        patch(
            "app.modules.catering.services.procurement_delivery_evidence.integration_service"
        ) as mock_integration,
    ):
        _configure_valid_database(mock_db, graph)
        mock_integration.execute.return_value = integration_result

        with pytest.raises(
            EntityValidationException,
            match="does not match the approved Purchase Order line",
        ):
            ProcurementDeliveryEvidenceResolver().get_receipt_status(
                graph.event_requirement
            )
