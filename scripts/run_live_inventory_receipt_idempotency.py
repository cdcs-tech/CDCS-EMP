"""
CDCS-EMP — CATERING-UAT-IDEMP-001

Explicitly opt-in live test for inventory receipt idempotency.

SAFETY:
- This script is never part of the ordinary pytest suite.
- It does not create/drop tables or run migrations.
- It verifies SQL Server and database identity before reading test records.
- It requires scenario-specific product, location, PO, PO-line, and user references.
- It intentionally creates receipt movements when explicitly executed.
- It does not delete test records or restore stock balances.

Do not execute this script during preparation.
"""

from __future__ import annotations

import os
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from threading import Barrier
from typing import Any


SCENARIO_ID = "CATERING-UAT-IDEMP-001"
EXPECTED_SERVER = "KASONGO"
EXPECTED_DATABASE = "CDCS_EMP_UAT"

OPT_IN_VARIABLE = "CDCS_EMP_LIVE_UAT_IDEMPOTENCY"
REQUIRED_ENVIRONMENT_VARIABLES = (
    "CATERING_UAT_USER_ID",
    "CATERING_UAT_PRODUCT_CODE",
    "CATERING_UAT_LOCATION_CODE",
    "CATERING_UAT_PO_REFERENCE",
    "CATERING_UAT_PO_LINE_REFERENCE",
    "CATERING_UAT_UNIT",
)

RECEIPT_QUANTITY_A = Decimal("2")
RECEIPT_QUANTITY_B = Decimal("3")
RECEIPT_TOTAL_QUANTITY = RECEIPT_QUANTITY_A + RECEIPT_QUANTITY_B
EXPECTED_VALUATION_PRICE = Decimal("2.50")
EXPECTED_VALUATION_CURRENCY = "USD"
EXPECTED_VALUATION_PRICE_BASIS = "PO_LINE_UNIT_PRICE"


def require_live_opt_in() -> None:
    """Fail closed unless live execution is explicitly enabled."""
    if os.environ.get(OPT_IN_VARIABLE) != "YES":
        raise RuntimeError(
            f"Live execution is disabled. Set {OPT_IN_VARIABLE}=YES "
            "only during the separately approved execution step."
        )

    missing = [
        name
        for name in REQUIRED_ENVIRONMENT_VARIABLES
        if not os.environ.get(name, "").strip()
    ]
    if missing:
        raise RuntimeError(
            "Missing required scenario configuration: "
            + ", ".join(missing)
        )


def verify_database_identity(db: Any) -> None:
    """Verify the actual connection before any receipt operation."""
    from sqlalchemy import text

    row = db.session.execute(
        text("SELECT @@SERVERNAME AS server_name, DB_NAME() AS database_name")
    ).one()

    actual_server = str(row.server_name or "").strip()
    actual_database = str(row.database_name or "").strip()

    # Permit a named SQL Server instance while still requiring KASONGO.
    server_host = actual_server.split("\\", maxsplit=1)[0].strip()

    if server_host.casefold() != EXPECTED_SERVER.casefold():
        raise RuntimeError(
            f"Wrong SQL Server. Expected {EXPECTED_SERVER}; "
            f"connected to {actual_server!r}. No receipt was submitted."
        )

    if actual_database.casefold() != EXPECTED_DATABASE.casefold():
        raise RuntimeError(
            f"Wrong database. Expected {EXPECTED_DATABASE}; "
            f"connected to {actual_database!r}. No receipt was submitted."
        )

    print(
        f"Database identity verified: "
        f"server={actual_server}, database={actual_database}"
    )


def build_authorized_movement_service():
    """
    Construct the movement service with the application's real authorization
    service, matching the authorization evaluation pattern in CateringModule.
    """
    from app.modules.catering.security.authorization import (
        CateringAuthorizationAdapter,
    )
    from app.modules.catering.services import StockMovementService
    from app.security.authorization import AuthorizationService

    user_id = os.environ["CATERING_UAT_USER_ID"].strip()

    class LiveUATSubject:
        """Explicit user identity used for real authorization evaluation."""

        def __init__(self, value: str):
            self.user_id = value

    subject = LiveUATSubject(user_id)

    def evaluate_catering_permission(candidate, permission_code):
        return AuthorizationService.authorize_execution(
            candidate.user_id,
            permission_code,
            context=candidate,
        )

    adapter = CateringAuthorizationAdapter(evaluate_catering_permission)

    return StockMovementService(authorization_adapter=adapter), subject


def get_balance_quantity(db, stock_item_id: int, location_id: int) -> Decimal:
    """
    Read the current balance without creating a row.

    Resolve the quantity field from the mapped model and fail closed if its
    name is unfamiliar. This prevents silently measuring the wrong field.
    """
    from sqlalchemy import inspect

    from app.modules.catering.models import StockBalance

    mapper = inspect(StockBalance)
    column_names = {column.key for column in mapper.columns}

    quantity_candidates = (
        "quantity",
        "quantity_on_hand",
        "balance_quantity",
        "available_quantity",
    )
    quantity_field = next(
        (name for name in quantity_candidates if name in column_names),
        None,
    )

    if quantity_field is None:
        raise RuntimeError(
            "Cannot identify the StockBalance quantity field safely. "
            f"Mapped columns: {sorted(column_names)}"
        )

    balance = (
        db.session.query(StockBalance)
        .filter_by(
            stock_item_id=stock_item_id,
            location_id=location_id,
        )
        .one_or_none()
    )

    if balance is None:
        return Decimal("0")

    return Decimal(str(getattr(balance, quantity_field)))


def load_scenario_references():
    """
    Resolve existing product, stock item, and location records.

    These lookups are read-only. The PO and line must already have been
    approved and prepared through the application's normal workflow.
    """
    from app.modules.catering.repositories import (
        InventoryLocationRepository,
        ProductRepository,
        StockItemRepository,
    )

    product_code = os.environ["CATERING_UAT_PRODUCT_CODE"].strip()
    location_code = os.environ["CATERING_UAT_LOCATION_CODE"].strip()

    product = ProductRepository().get_by_code(product_code)
    if product is None:
        raise RuntimeError(f"Scenario product {product_code!r} was not found.")
    if getattr(product, "is_deleted", False):
        raise RuntimeError(f"Scenario product {product_code!r} is deleted.")

    stock_item = StockItemRepository().get_by_product_id(product.id)
    if stock_item is None:
        raise RuntimeError(
            f"No StockItem exists for scenario product {product_code!r}."
        )
    if getattr(stock_item, "is_deleted", False):
        raise RuntimeError(
            f"StockItem for scenario product {product_code!r} is deleted."
        )

    location = InventoryLocationRepository().get_by_code(location_code)
    if location is None:
        raise RuntimeError(
            f"Scenario inventory location {location_code!r} was not found."
        )
    if getattr(location, "is_deleted", False):
        raise RuntimeError(
            f"Scenario inventory location {location_code!r} is deleted."
        )

    return product, stock_item, location


def validate_purchase_order_references() -> tuple[str, str, Decimal]:
    """Fail closed unless the configured approved PO and line match."""
    from app.modules.procurement.models import PurchaseOrder, PurchaseOrderLine

    po_reference = os.environ["CATERING_UAT_PO_REFERENCE"].strip()
    line_reference = os.environ["CATERING_UAT_PO_LINE_REFERENCE"].strip()
    product_code = os.environ["CATERING_UAT_PRODUCT_CODE"].strip()
    configured_unit = os.environ["CATERING_UAT_UNIT"].strip()
    prefix = "PO-LINE-"

    if not line_reference.startswith(prefix):
        raise RuntimeError(
            "CATERING_UAT_PO_LINE_REFERENCE must use PO-LINE-{guid}."
        )

    line_guid_text = line_reference[len(prefix):].strip()
    try:
        line_guid = uuid.UUID(line_guid_text)
    except (AttributeError, TypeError, ValueError) as exc:
        raise RuntimeError(
            "Configured PO line reference must end in a valid GUID."
        ) from exc

    if line_reference != f"{prefix}{line_guid}":
        raise RuntimeError(
            "Purchase Order Line reference is not in canonical form "
            "'PO-LINE-{line.guid}'. No receipt was submitted."
        )

    purchase_order = (
        PurchaseOrder.query
        .filter_by(reference=po_reference)
        .one_or_none()
    )
    if purchase_order is None:
        raise RuntimeError(f"Configured PO {po_reference!r} was not found.")
    if getattr(purchase_order, "is_deleted", False):
        raise RuntimeError(f"Configured PO {po_reference!r} is deleted.")
    if purchase_order.status != "APPROVED":
        raise RuntimeError(
            f"Configured PO must be APPROVED; found {purchase_order.status!r}."
        )

    purchase_order_line = (
        PurchaseOrderLine.query
        .filter_by(guid=line_guid)
        .one_or_none()
    )
    if purchase_order_line is None:
        raise RuntimeError("Configured PO line GUID was not found.")
    if getattr(purchase_order_line, "is_deleted", False):
        raise RuntimeError("Configured PO line is deleted.")
    if purchase_order_line.purchase_order_id != purchase_order.id:
        raise RuntimeError(
            "Configured PO line does not belong to the configured PO."
        )
    if purchase_order_line.stock_item_reference != product_code:
        raise RuntimeError(
            "Configured PO line does not reference the configured product."
        )
    if purchase_order_line.unit != configured_unit:
        raise RuntimeError(
            "Configured PO line unit does not match CATERING_UAT_UNIT."
        )

    if purchase_order_line.quantity is None:
        raise RuntimeError("Configured PO line has no ordered quantity.")

    try:
        ordered_quantity = Decimal(str(purchase_order_line.quantity))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise RuntimeError(
            "Configured PO line ordered quantity is invalid."
        ) from exc

    if not ordered_quantity.is_finite() or ordered_quantity <= 0:
        raise RuntimeError(
            "Configured PO line ordered quantity must be finite and positive."
        )

    if purchase_order_line.unit_price is None:
        raise RuntimeError("Configured PO line has no stored unit price.")

    try:
        unit_price = Decimal(str(purchase_order_line.unit_price))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise RuntimeError(
            "Configured PO line unit price is invalid."
        ) from exc

    if unit_price != EXPECTED_VALUATION_PRICE:
        raise RuntimeError(
            "Configured PO line unit price does not match the scenario's "
            f"expected price {EXPECTED_VALUATION_PRICE}."
        )

    if purchase_order.currency != EXPECTED_VALUATION_CURRENCY:
        raise RuntimeError(
            "Configured PO currency does not match the scenario's expected "
            f"currency {EXPECTED_VALUATION_CURRENCY!r}."
        )

    return po_reference, line_reference, ordered_quantity


def verify_remaining_po_line_quantity(
    *,
    po_reference: str,
    po_line_reference: str,
    product_reference: str,
    ordered_quantity: Decimal,
    expected_unit: str,
    check_remaining_quantity: bool = True,
) -> tuple[Decimal, int]:
    """Verify existing receipt quantity before starting the live scenario."""
    from app.core.integration import IntegrationRequest
    from app.modules.procurement.integration import (
        INVENTORY_INTEGRATION_PROVIDER,
        INVENTORY_QUERY_PURCHASE_ORDER_LINE_RECEIPT_STATUS_OPERATION,
        PurchaseOrderLineReceiptStatusRequest,
    )
    from app.modules.procurement.integration.providers.inventory import (
        InventoryReceiptIntegrationProvider,
    )

    request_payload = PurchaseOrderLineReceiptStatusRequest(
        purchase_order_reference=po_reference,
        purchase_order_line_reference=po_line_reference,
        stock_item_reference=product_reference,
    )

    provider = InventoryReceiptIntegrationProvider()
    request = IntegrationRequest(
        provider=INVENTORY_INTEGRATION_PROVIDER,
        operation=INVENTORY_QUERY_PURCHASE_ORDER_LINE_RECEIPT_STATUS_OPERATION,
        payload=request_payload,
        metadata={"module": "PROCUREMENT"},
    )
    response = provider.execute(request)

    if not response.success:
        raise RuntimeError(
            "Could not verify existing PO-line receipts through the "
            f"authoritative status provider: {response.message}"
        )

    data = response.data
    if not isinstance(data, dict):
        raise RuntimeError(
            "Receipt-status provider returned an unexpected response shape; "
            "cannot verify remaining PO-line quantity safely."
        )

    if data.get("success") is not True:
        raise RuntimeError(
            "Receipt-status query did not report success in its response data."
        )

    if data.get("purchase_order_reference") != po_reference:
        raise RuntimeError(
            "Receipt-status response PO reference does not match the request."
        )

    if data.get("purchase_order_line_reference") != po_line_reference:
        raise RuntimeError(
            "Receipt-status response PO-line reference does not match "
            "the request."
        )

    received_value = data.get("received_quantity")
    returned_unit = data.get("unit")

    if received_value is None:
        raise RuntimeError(
            "Receipt-status result omitted received_quantity."
        )

    try:
        received_quantity = Decimal(str(received_value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise RuntimeError(
            "Receipt-status result contains an invalid received_quantity."
        ) from exc

    if not received_quantity.is_finite() or received_quantity < 0:
        raise RuntimeError(
            "Receipt-status received_quantity must be finite and nonnegative."
        )

    receipt_count_value = data.get("receipt_count")
    has_receipts = data.get("has_receipts")

    if (
        isinstance(receipt_count_value, bool)
        or not isinstance(receipt_count_value, int)
        or receipt_count_value < 0
    ):
        raise RuntimeError(
            "Receipt-status result contains an invalid receipt_count."
        )

    if not isinstance(has_receipts, bool):
        raise RuntimeError(
            "Receipt-status result contains an invalid has_receipts value."
        )

    if has_receipts != (receipt_count_value > 0):
        raise RuntimeError(
            "Receipt-status has_receipts conflicts with receipt_count."
        )

    # Purpose: Reject receipt history inconsistent with the domain contract.
    if (receipt_count_value == 0) != (received_quantity == 0):
        raise RuntimeError(
            "Receipt-status quantity conflicts with receipt_count."
        )

    if returned_unit != expected_unit:
        raise RuntimeError(
            f"Receipt-status unit mismatch: expected {expected_unit!r}, "
            f"received {returned_unit!r}."
        )

    remaining_quantity = ordered_quantity - received_quantity

    if check_remaining_quantity:
        if remaining_quantity < RECEIPT_TOTAL_QUANTITY:
            raise RuntimeError(
                "Insufficient remaining PO-line quantity for the planned test: "
                f"remaining={remaining_quantity}, "
                f"required={RECEIPT_TOTAL_QUANTITY} {expected_unit}."
            )

        print(
            "PO-line quantity preflight passed: "
            f"ordered={ordered_quantity}, received={received_quantity}, "
            f"remaining={remaining_quantity}, "
            f"planned={RECEIPT_TOTAL_QUANTITY} {expected_unit}"
        )

    return received_quantity, receipt_count_value


def make_receipt(
    *,
    key: str,
    receiving_reference: str,
    quantity: Decimal,
    valuation_price: Decimal,
    valuation_currency: str,
    valuation_price_basis: str,
):
    """Build a receipt request using only explicitly supplied scenario refs."""
    from app.modules.procurement.integration import PurchaseOrderReceiptRequest

    return PurchaseOrderReceiptRequest(
        purchase_order_reference=os.environ[
            "CATERING_UAT_PO_REFERENCE"
        ].strip(),
        purchase_order_line_reference=os.environ[
            "CATERING_UAT_PO_LINE_REFERENCE"
        ].strip(),
        stock_item_reference=os.environ[
            "CATERING_UAT_PRODUCT_CODE"
        ].strip(),
        inventory_location_reference=os.environ[
            "CATERING_UAT_LOCATION_CODE"
        ].strip(),
        quantity_received=quantity,
        unit=os.environ.get("CATERING_UAT_UNIT", "").strip(),
        received_at=datetime.now(timezone.utc),
        receiving_reference=receiving_reference,
        idempotency_key=key,
        valuation_unit_price=valuation_price,
        valuation_currency=valuation_currency,
        valuation_price_basis=valuation_price_basis,
        notes=f"{SCENARIO_ID} controlled live idempotency test",
    )


def submit_receipt(
    app,
    db,
    *,
    key: str,
    receiving_reference: str,
    quantity: Decimal,
    valuation_price: Decimal,
    valuation_currency: str,
    valuation_price_basis: str,
    barrier: Barrier | None = None,
) -> tuple[bool, int | None]:
    """
    Submit through the real Procurement inventory integration provider.

    The database session is scoped to this application context/thread.
    A successful response must include a valid movement ID.
    """
    from app.core.integration import IntegrationRequest
    from app.modules.procurement.integration import (
        INVENTORY_INTEGRATION_PROVIDER,
        INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION,
    )
    from app.modules.procurement.integration.providers.inventory import (
        InventoryReceiptIntegrationProvider,
    )

    with app.app_context():
        try:
            service, subject = build_authorized_movement_service()
            provider = InventoryReceiptIntegrationProvider(
                movement_service=service,
            )

            payload = make_receipt(
                key=key,
                receiving_reference=receiving_reference,
                quantity=quantity,
                valuation_price=valuation_price,
                valuation_currency=valuation_currency,
                valuation_price_basis=valuation_price_basis,
            )

            request = IntegrationRequest(
                provider=INVENTORY_INTEGRATION_PROVIDER,
                operation=INVENTORY_RECEIVE_PURCHASE_ORDER_OPERATION,
                payload=payload,
                metadata={
                    "module": "PROCUREMENT",
                    "subject": subject,
                    "operation": "procurement.purchase_order.receive",
                },
            )

            if barrier is not None:
                barrier.wait(timeout=20)

            response = provider.execute(request)

            if not response.success:
                print(
                    f"Receipt submission failed for key {key!r}: "
                    f"{response.message}"
                )
                return False, None

            response_data = response.data
            if not isinstance(response_data, dict):
                raise RuntimeError(
                    f"Receipt submission for key {key!r} returned an "
                    "unexpected response data shape."
                )

            movement_id = response_data.get("stock_movement_id")
            if movement_id is None:
                raise RuntimeError(
                    f"Receipt submission for key {key!r} succeeded, but "
                    "the provider did not return a movement ID."
                )

            try:
                movement_id = int(movement_id)
            except (TypeError, ValueError) as exc:
                raise RuntimeError(
                    f"Receipt submission for key {key!r} returned an "
                    f"invalid movement ID: {movement_id!r}."
                ) from exc

            if movement_id <= 0:
                raise RuntimeError(
                    f"Receipt submission for key {key!r} returned a "
                    f"non-positive movement ID: {movement_id}."
                )

            return True, movement_id
        finally:
            db.session.remove()


def verify_receipt_key(
    db,
    *,
    key: str,
    expected_quantity: Decimal,
    expected_price: Decimal,
    expected_currency: str,
    expected_po_reference: str,
    expected_po_line_reference: str,
    expected_stock_item_id: int,
    expected_location_id: int,
    expected_receiving_reference: str,
    expected_unit: str,
) -> int:
    """
    Independently read the idempotency record and its movement.

    Use a new SQLAlchemy Session instance so verification does not rely on
    objects held in the application's scoped-session identity map.
    """
    from app.modules.catering.models import StockMovement
    from app.modules.catering.models.inventory_receipt_idempotency import (
        InventoryReceiptIdempotency,
    )

    db.session.remove()

    session_factory = getattr(db.session, "session_factory", None)
    if not callable(session_factory):
        raise RuntimeError(
            "Cannot create an independent SQLAlchemy Session from the "
            "configured scoped session. Persistence verification stopped."
        )

    # Purpose: Verify persisted rows through a distinct ORM Session instance.
    with session_factory() as session:
        records = (
            session.query(InventoryReceiptIdempotency)
            .filter_by(idempotency_key=key)
            .all()
        )

        if len(records) != 1:
            raise AssertionError(
                f"Expected one idempotency record for {key!r}; "
                f"found {len(records)}."
            )

        record = records[0]

        if record.purchase_order_reference != expected_po_reference:
            raise AssertionError(
                f"PO reference mismatch for {key!r}: "
                f"{record.purchase_order_reference!r}."
            )
        if (
            record.purchase_order_line_reference
            != expected_po_line_reference
        ):
            raise AssertionError(
                f"PO-line reference mismatch for {key!r}: "
                f"{record.purchase_order_line_reference!r}."
            )

        movement = session.get(StockMovement, record.stock_movement_id)
        if movement is None:
            raise AssertionError(
                f"Idempotency record {key!r} points to no movement."
            )

        if movement.stock_item_id != expected_stock_item_id:
            raise AssertionError(
                f"Stock item mismatch for {key!r}: "
                f"{movement.stock_item_id!r}."
            )
        if movement.location_id != expected_location_id:
            raise AssertionError(
                f"Location mismatch for {key!r}: {movement.location_id!r}."
            )
        if movement.reference != expected_receiving_reference:
            raise AssertionError(
                f"Receiving reference mismatch for {key!r}: "
                f"{movement.reference!r}."
            )
        if movement.unit != expected_unit:
            raise AssertionError(
                f"Movement unit mismatch for {key!r}: {movement.unit!r}."
            )

        if Decimal(str(movement.quantity)) != expected_quantity:
            raise AssertionError(
                f"Movement quantity mismatch for {key!r}: "
                f"{movement.quantity!r}."
            )

        if movement.status != "POSTED":
            raise AssertionError(
                f"Expected POSTED movement for {key!r}; "
                f"found {movement.status!r}."
            )

        if Decimal(str(movement.valuation_unit_price)) != expected_price:
            raise AssertionError(
                f"Valuation price changed for {key!r}: "
                f"{movement.valuation_unit_price!r}."
            )

        if movement.valuation_currency != expected_currency:
            raise AssertionError(
                f"Valuation currency changed for {key!r}: "
                f"{movement.valuation_currency!r}."
            )

        if (
            movement.valuation_price_basis
            != EXPECTED_VALUATION_PRICE_BASIS
        ):
            raise AssertionError(
                f"Valuation price basis mismatch for {key!r}: "
                f"{movement.valuation_price_basis!r}."
            )

        movement_id = movement.id
        movement_quantity = movement.quantity
        movement_price = movement.valuation_unit_price
        movement_currency = movement.valuation_currency

    print(
        f"Verified key={key!r}, movement_id={movement_id}, "
        f"quantity={movement_quantity}, "
        f"price={movement_price} {movement_currency}"
    )

    return movement_id


def run_live_test(app, db) -> None:
    """Run the opt-in scenario. Calling this function writes receipt records."""
    verify_database_identity(db)

    # Resolve and validate all scenario records before submitting any receipt.
    product, stock_item, location = load_scenario_references()
    po_reference, po_line_reference, ordered_quantity = (
        validate_purchase_order_references()
    )

    configured_unit = os.environ["CATERING_UAT_UNIT"].strip()
    product_reference = os.environ["CATERING_UAT_PRODUCT_CODE"].strip()

    initial_received_quantity, initial_receipt_count = (
        verify_remaining_po_line_quantity(
            po_reference=po_reference,
            po_line_reference=po_line_reference,
            product_reference=product_reference,
            ordered_quantity=ordered_quantity,
            expected_unit=configured_unit,
        )
    )

    print(f"Scenario: {SCENARIO_ID}")
    print(f"Product: {product.id} / {product.code}")
    print(f"Stock item: {stock_item.id}")
    print(f"Location: {location.id} / {location.code}")
    print(f"PO reference supplied: {po_reference}")
    print(f"PO line reference supplied: {po_line_reference}")

    initial_balance = get_balance_quantity(
        db,
        stock_item.id,
        location.id,
    )

    prefix = (
        f"{SCENARIO_ID}-"
        f"{datetime.now(timezone.utc):%Y%m%dT%H%M%S}"
    )
    key_a = f"{prefix}-SEQUENTIAL"
    key_b = f"{prefix}-CONCURRENT"
    ref_a = f"{prefix}-GRN-A"
    ref_b = f"{prefix}-GRN-B"

    qty_a = RECEIPT_QUANTITY_A
    price_a = EXPECTED_VALUATION_PRICE
    currency_a = EXPECTED_VALUATION_CURRENCY

    # Case A: create one receipt, then submit an identical idempotency retry.
    first_ok, first_movement_id = submit_receipt(
        app,
        db,
        key=key_a,
        receiving_reference=ref_a,
        quantity=qty_a,
        valuation_price=price_a,
        valuation_currency=currency_a,
        valuation_price_basis=EXPECTED_VALUATION_PRICE_BASIS,
    )
    if not first_ok:
        raise RuntimeError("Initial receipt failed; stopping the scenario.")
    if first_movement_id is None:
        raise AssertionError(
            "Initial receipt succeeded without returning a movement ID."
        )

    retry_ok, retry_movement_id = submit_receipt(
        app,
        db,
        key=key_a,
        receiving_reference=ref_a,
        quantity=qty_a,
        valuation_price=price_a,
        valuation_currency=currency_a,
        valuation_price_basis=EXPECTED_VALUATION_PRICE_BASIS,
    )
    if not retry_ok:
        raise RuntimeError("Sequential idempotency retry failed.")
    if retry_movement_id is None:
        raise AssertionError(
            "Sequential retry succeeded without returning a movement ID."
        )

    movement_a_id = verify_receipt_key(
        db,
        key=key_a,
        expected_quantity=qty_a,
        expected_price=price_a,
        expected_currency=currency_a,
        expected_po_reference=po_reference,
        expected_po_line_reference=po_line_reference,
        expected_stock_item_id=stock_item.id,
        expected_location_id=location.id,
        expected_receiving_reference=ref_a,
        expected_unit=configured_unit,
    )

    if first_movement_id != movement_a_id:
        raise AssertionError(
            "Initial receipt response movement ID differs from the "
            "persisted idempotency movement."
        )
    if retry_movement_id != movement_a_id:
        raise AssertionError(
            "Sequential retry returned a different movement ID."
        )

    # Case B: conflicting valuation inputs must not alter the original receipt.
    conflict_ok, conflict_movement_id = submit_receipt(
        app,
        db,
        key=key_a,
        receiving_reference=ref_a,
        quantity=qty_a,
        valuation_price=Decimal("999.99"),
        valuation_currency="SSP",
        valuation_price_basis=EXPECTED_VALUATION_PRICE_BASIS,
    )
    if not conflict_ok:
        raise RuntimeError("Conflicting sequential retry failed.")
    if conflict_movement_id is None:
        raise AssertionError(
            "Conflicting retry succeeded without returning a movement ID."
        )
    if conflict_movement_id != movement_a_id:
        raise AssertionError(
            "Conflicting retry returned a different movement ID."
        )

    verified_movement_a_id = verify_receipt_key(
        db,
        key=key_a,
        expected_quantity=qty_a,
        expected_price=price_a,
        expected_currency=currency_a,
        expected_po_reference=po_reference,
        expected_po_line_reference=po_line_reference,
        expected_stock_item_id=stock_item.id,
        expected_location_id=location.id,
        expected_receiving_reference=ref_a,
        expected_unit=configured_unit,
    )
    if verified_movement_a_id != movement_a_id:
        raise AssertionError(
            "Conflicting retry changed the persisted idempotency movement."
        )

    # Case C: two concurrent callers use one new idempotency key.
    qty_b = RECEIPT_QUANTITY_B
    price_b = EXPECTED_VALUATION_PRICE
    currency_b = EXPECTED_VALUATION_CURRENCY
    barrier = Barrier(2)

    def concurrent_call() -> tuple[bool, int | None]:
        return submit_receipt(
            app,
            db,
            key=key_b,
            receiving_reference=ref_b,
            quantity=qty_b,
            valuation_price=price_b,
            valuation_currency=currency_b,
            valuation_price_basis=EXPECTED_VALUATION_PRICE_BASIS,
            barrier=barrier,
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(concurrent_call),
            executor.submit(concurrent_call),
        ]
        concurrent_results = [future.result() for future in futures]

    if not all(success for success, _movement_id in concurrent_results):
        raise AssertionError(
            "At least one concurrent submission returned failure. "
            "Inspect the database and application logs before any rerun."
        )

    concurrent_movement_ids = [
        movement_id
        for _success, movement_id in concurrent_results
    ]

    if any(movement_id is None for movement_id in concurrent_movement_ids):
        raise AssertionError(
            "A successful concurrent submission returned no movement ID."
        )

    if len(set(concurrent_movement_ids)) != 1:
        raise AssertionError(
            "Concurrent callers returned different movement IDs: "
            f"{concurrent_movement_ids!r}."
        )

    movement_b_id = verify_receipt_key(
        db,
        key=key_b,
        expected_quantity=qty_b,
        expected_price=price_b,
        expected_currency=currency_b,
        expected_po_reference=po_reference,
        expected_po_line_reference=po_line_reference,
        expected_stock_item_id=stock_item.id,
        expected_location_id=location.id,
        expected_receiving_reference=ref_b,
        expected_unit=configured_unit,
    )

    if concurrent_movement_ids[0] != movement_b_id:
        raise AssertionError(
            "Concurrent caller movement ID does not match the "
            "persisted idempotency movement."
        )

    if movement_b_id == movement_a_id:
        raise AssertionError(
            "Independent idempotency keys unexpectedly share a movement."
        )

    final_received_quantity, final_receipt_count = (
        verify_remaining_po_line_quantity(
            po_reference=po_reference,
            po_line_reference=po_line_reference,
            product_reference=product_reference,
            ordered_quantity=ordered_quantity,
            expected_unit=configured_unit,
            check_remaining_quantity=False,
        )
    )

    expected_received_quantity = (
        initial_received_quantity + RECEIPT_TOTAL_QUANTITY
    )
    expected_receipt_count = initial_receipt_count + 2

    if final_received_quantity != expected_received_quantity:
        raise AssertionError(
            "PO-line received quantity mismatch: "
            f"initial={initial_received_quantity}, "
            f"expected={expected_received_quantity}, "
            f"actual={final_received_quantity}."
        )

    if final_receipt_count != expected_receipt_count:
        raise AssertionError(
            "PO-line receipt count mismatch: "
            f"initial={initial_receipt_count}, "
            f"expected={expected_receipt_count}, "
            f"actual={final_receipt_count}."
        )

    print(
        "PO-line receipt totals verified: "
        f"received={final_received_quantity} {configured_unit}, "
        f"receipt_count={final_receipt_count}"
    )

    final_balance = get_balance_quantity(
        db,
        stock_item.id,
        location.id,
    )
    expected_balance = initial_balance + qty_a + qty_b

    if final_balance != expected_balance:
        raise AssertionError(
            f"Balance mismatch: initial={initial_balance}, "
            f"expected={expected_balance}, actual={final_balance}."
        )

    print("\nPASS — receipt idempotency scenario completed.")
    print(f"Initial balance: {initial_balance}")
    print(f"Expected final balance: {expected_balance}")
    print(f"Actual final balance: {final_balance}")
    print(f"Sequential movement ID: {movement_a_id}")
    print(f"Concurrent movement ID: {movement_b_id}")
    print("Evidence: retain this output with the scenario execution log.")


def main() -> int:
    try:
        require_live_opt_in()

        # Import only after the explicit opt-in check.
        from app import create_app
        from app.extensions import db

        app = create_app("development")

        with app.app_context():
            verify_database_identity(db)

            # Run the scenario only after the connection identity has passed.
            # Keep all database operations inside the Flask application context.
            run_live_test(app, db)

        return 0

    except Exception as exc:
        print(
            f"\nFAIL-CLOSED — {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        print(
            "Do not blindly rerun. Inspect database records and logs first.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
