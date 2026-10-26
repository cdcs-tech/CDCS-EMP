"""
CDCS-EMP Phase 2.2
Procurement ↔ Finance Integration — Stage 7

End-to-end verification of the complete:

Purchase Order
    ↓
Procurement Approval
    ↓
Procurement Finance Commitment Registration
    ↓
Procurement Transaction Commit
    ↓
Post-Commit Finance Delivery
    ↓
Finance Commitment COMMITTED
"""

from datetime import date
from decimal import Decimal

import pytest

from app.extensions import db

from app.core.execution.context import (
    ExecutionContext,
)

from app.core.integration import (
    IntegrationLifecycle,
    IntegrationRequest,
    IntegrationResponse,
    IntegrationResult,
    IntegrationService,
)

from app.core.security.module_permissions import (
    ModulePermissionSynchronizer,
)

from app.core.startup import (
    initialize_modules,
)

from app.modules.procurement.commands.purchase_order import (
    ApprovePurchaseOrderCommand,
    SubmitPurchaseOrderCommand,
)

from app.modules.procurement.integration.contracts import (
    FINANCE_INTEGRATION_PROVIDER,
    FINANCE_PROCUREMENT_COMMITMENT_OPERATION,
)

from app.modules.procurement.integration.post_commit import (
    ProcurementFinancePostCommitExecutor,
)

from app.modules.procurement.models.purchase_order import (
    PurchaseOrder,
)

from app.modules.procurement.models.purchase_order_line import (
    PurchaseOrderLine,
)

from app.modules.procurement.models.purchase_request import (
    PurchaseRequest,
)

from app.modules.procurement.models.purchase_requirement import (
    PurchaseRequirement,
)

from app.modules.procurement.models.supplier import (
    Supplier,
)

from app.modules.procurement.repositories.finance_commitment import (
    ProcurementFinanceCommitmentRepository,
)

from app.modules.procurement.services.finance_commitment import (
    ProcurementFinanceCommitmentService,
)


class RecordingFinanceIntegrationService(
    IntegrationService
):
    """
    Test Finance provider that records every integration
    request and returns a successful response.
    """

    def __init__(self):
        super().__init__()

        self.requests = []

    def execute(
        self,
        request: IntegrationRequest,
    ):
        self.requests.append(
            request
        )

        response = IntegrationResponse(
            success=True,
            status_code=200,
            data={
                "external_reference": (
                    "FIN-E2E-001"
                )
            },
            message=(
                "Finance integration accepted."
            ),
            metadata={
                "stage": "stage-7-e2e"
            },
            request_id=request.request_id,
        )

        return IntegrationResult(
            request=request,
            response=response,
        )


@pytest.fixture
def finance_e2e_environment(
    app,
    admin_user,
):
    """
    Configure the real Stage 7 Finance integration path
    while using a recording Finance provider.

    The application's authoritative ModuleManager is
    retrieved from ApplicationLifecycle rather than from
    CommandDispatcher.
    """

    lifecycle = app.extensions[
        "application_lifecycle"
    ]

    module_manager = (
        lifecycle.module_manager
    )

    assert module_manager is not None

    active_modules = (
        module_manager.get_active_modules()
    )

    ModulePermissionSynchronizer(
        role_name="Administrator",
    ).synchronize(
        modules=active_modules,
    )

    command_dispatcher = app.extensions[
        "command_dispatcher"
    ]

    finance_service = (
        RecordingFinanceIntegrationService()
    )

    integration_lifecycle = (
        IntegrationLifecycle(
            service=finance_service,
        )
    )

    commitment_service = (
        ProcurementFinanceCommitmentService(
            integration_lifecycle=(
                integration_lifecycle
            ),
        )
    )

    post_commit_executor = (
        ProcurementFinancePostCommitExecutor(
            commitment_service=(
                commitment_service
            ),
        )
    )

    original_post_commit_executor = (
        command_dispatcher.post_commit_executor
    )

    command_dispatcher.set_post_commit_executor(
        post_commit_executor
    )

    try:
        yield {
            "command_dispatcher": (
                command_dispatcher
            ),
            "finance_service": (
                finance_service
            ),
            "integration_lifecycle": (
                integration_lifecycle
            ),
            "commitment_service": (
                commitment_service
            ),
        }

    finally:
        command_dispatcher.set_post_commit_executor(
            original_post_commit_executor
        )


def test_purchase_order_approval_to_finance_commitment_e2e(
    app,
    admin_user,
    finance_e2e_environment,
):
    """
    Verify the complete Procurement → Finance lifecycle.

    The test verifies that:

    1. A Purchase Order can be submitted.
    2. The Purchase Order can be approved.
    3. Approval registers a Procurement-owned Finance commitment.
    4. The Procurement transaction commits before Finance delivery.
    5. Finance receives the commitment post-commit.
    6. Successful Finance delivery results in COMMITTED.
    7. The durable idempotency key is preserved.
    8. Finance receives exactly one integration request.
    9. The Finance request receives its own enterprise request_id.
    """

    environment = (
        finance_e2e_environment
    )

    command_dispatcher = (
        environment["command_dispatcher"]
    )

    finance_service = (
        environment["finance_service"]
    )

    # -----------------------------------------------------
    # Arrange
    # -----------------------------------------------------

    purchase_requirement = (
        PurchaseRequirement(
            reference=(
                "REQ-E2E-FIN-001"
            ),
            description=(
                "Stage 7 Finance integration "
                "verification requirement"
            ),
        )
    )

    db.session.add(
        purchase_requirement
    )

    db.session.flush()

    purchase_request = (
        PurchaseRequest(
            reference=(
                "PR-E2E-FIN-001"
            ),
            purchase_requirement_id=(
                purchase_requirement.id
            ),
            request_date=date.today(),
            justification=(
                "Stage 7 end-to-end verification"
            ),
        )
    )

    supplier = Supplier(
        name="E2E Finance Supplier",
        code="SUP-E2E-FIN-001",
        supplier_type="LOCAL",
    )

    db.session.add_all(
        [
            purchase_request,
            supplier,
        ]
    )

    db.session.flush()

    purchase_order = PurchaseOrder(
        supplier_id=supplier.id,
        reference="PO-E2E-FIN-001",
        order_date=date.today(),
        currency="USD",
        purchase_request_id=(
            purchase_request.id
        ),
    )

    db.session.add(
        purchase_order
    )

    db.session.flush()

    first_line = PurchaseOrderLine(
        purchase_order_id=(
            purchase_order.id
        ),
        description="E2E Finance item A",
        item_reference="E2E-A",
        quantity=Decimal("2.000"),
        unit="EA",
        unit_price=Decimal("100.00"),
        total_amount=Decimal("200.00"),
    )

    second_line = PurchaseOrderLine(
        purchase_order_id=(
            purchase_order.id
        ),
        description="E2E Finance item B",
        item_reference="E2E-B",
        quantity=Decimal("3.000"),
        unit="EA",
        unit_price=Decimal("50.00"),
        total_amount=Decimal("150.00"),
    )

    db.session.add_all(
        [
            first_line,
            second_line,
        ]
    )

    db.session.commit()

    # -----------------------------------------------------
    # Submit Purchase Order
    # -----------------------------------------------------

    submit_context = ExecutionContext(
        request_id="REQ-E2E-SUBMIT-001",
        correlation_id="CORR-E2E-FIN-001",
        trace_id="TRACE-E2E-FIN-001",
        module_name="procurement",
        operation="procurement.purchase_order.submit",
        user_id=admin_user.id,
    )

    submit_result = (
        command_dispatcher.dispatch(
            SubmitPurchaseOrderCommand(
                purchase_order_id=(
                    purchase_order.id
                ),
            ),
            submit_context,
        )
    )

    assert submit_result.is_success()

    db.session.expire_all()

    purchase_order = (
        db.session.get(
            PurchaseOrder,
            purchase_order.id,
        )
    )

    assert purchase_order.status == "SUBMITTED"

    # -----------------------------------------------------
    # Approve Purchase Order
    # -----------------------------------------------------

    approval_context = ExecutionContext(
        request_id="REQ-E2E-APPROVAL-001",
        correlation_id="CORR-E2E-FIN-001",
        trace_id="TRACE-E2E-FIN-001",
        module_name="procurement",
        operation="procurement.purchase_order.approve",
        user_id=admin_user.id,
    )

    approval_result = (
        command_dispatcher.dispatch(
            ApprovePurchaseOrderCommand(
                purchase_order_id=(
                    purchase_order.id
                ),
            ),
            approval_context,
        )
    )

    assert approval_result.is_success()

    db.session.expire_all()

    purchase_order = (
        db.session.get(
            PurchaseOrder,
            purchase_order.id,
        )
    )

    assert purchase_order.status == "APPROVED"

    # -----------------------------------------------------
    # Verify Finance Commitment
    # -----------------------------------------------------

    commitment_repository = (
        ProcurementFinanceCommitmentRepository()
    )

    commitment = (
        commitment_repository.get_by_purchase_order_id(
            purchase_order.id
        )
    )

    assert commitment is not None

    assert commitment.status == "COMMITTED", (
        f"Finance delivery failed: "
        f"{commitment.last_error!r}"
    )

    # -----------------------------------------------------
    # Verify Durable Idempotency
    # -----------------------------------------------------

    assert commitment.idempotency_key

    # -----------------------------------------------------
    # Verify Finance Delivery
    # -----------------------------------------------------

    assert len(
        finance_service.requests
    ) == 1

    finance_request = (
        finance_service.requests[0]
    )

    assert (
        finance_request.provider
        == FINANCE_INTEGRATION_PROVIDER
    )

    assert (
        finance_request.operation
        == FINANCE_PROCUREMENT_COMMITMENT_OPERATION
    )

    assert (
        finance_request.payload.idempotency_key
        == commitment.idempotency_key
    )

    # -----------------------------------------------------
    # Verify Enterprise Request Identity
    # -----------------------------------------------------

    assert (
        finance_request.request_id
        != approval_context.request_id
    )
