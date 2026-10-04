"""C6.8 full pilot end-to-end business-flow acceptance test."""

from datetime import date, datetime, timezone
from decimal import Decimal

from app.core.execution import ExecutionContext
from app.extensions import db
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.modules.catering.commands import RecognizeCateringRevenueCommand
from app.modules.catering.models import (
    CateringEvent,
    CateringExpenseCostAssociation,
    CateringPurchaseRequirement,
    CateringQuotation,
    CateringRequest,
    CateringRevenue,
    Customer,
    EventRequirement,
    InventoryLocation,
    Product,
    ProductCategory,
    StockItem,
)
from app.modules.catering.repositories.catering_event import (
    CateringEventRepository,
)
from app.modules.catering.repositories.catering_revenue import (
    CateringRevenueRepository,
)
from app.modules.catering.repositories.expense_cost_association import (
    CateringExpenseCostAssociationRepository,
)
from app.modules.catering.security.authorization import (
    CateringAuthorizationAdapter,
)
from app.modules.catering.services.catering_event import CateringEventService
from app.modules.catering.services.catering_quotation_event_coordination import (
    CateringQuotationEventCoordinationService,
)
from app.modules.catering.services.event_profitability import (
    EventProfitabilityService,
)
from app.modules.catering.services.procurement_handoff import (
    CateringProcurementHandoffService,
)
from app.modules.catering.workflows import CateringRevenueWorkflow
from app.modules.expense.commands import ApproveExpenseCommand
from app.modules.expense.models import Expense, ExpenseClassification
from app.modules.expense.workflows.expense import APPROVED, SUBMITTED
from app.modules.finance.models import FinanceRevenue
from app.modules.procurement.commands import ReceivePurchaseOrderCommand
from app.modules.procurement.models import (
    PurchaseOrder,
    PurchaseRequest,
    Supplier,
)
from app.modules.procurement.services.purchase_flow import (
    ProcurementPurchaseFlowService,
)
from app.modules.procurement.services.purchase_order import (
    PurchaseOrderService,
)
from app.modules.procurement.services.purchase_request import (
    PurchaseRequestService,
)
from app.security.authorization import AuthorizationService
from app.modules.expense.repositories.expense import ExpenseRepository


def test_full_pilot_business_flow_executes_across_module_boundaries(
    app,
    admin_user,
):
    """Validate the complete C6.1-C6.7 pilot business flow."""

    with app.app_context():
        administrator_role = (
            db.session.query(Role)
            .filter_by(name="Administrator")
            .one()
        )

        required_permissions = [
            (
                "CATERING",
                "CATERING.CATERING_REVENUE.RECOGNIZE",
            ),
            (
                "CATERING",
                "CATERING.CATERING_PURCHASE_REQUIREMENT.CREATE",
            ),
            (
                "CATERING",
                "CATERING.CATERING_PURCHASE_REQUIREMENT.SUBMIT_TO_PROCUREMENT",
            ),
            (
                "CATERING",
                "CATERING.CATERING_EVENT.QUOTE",
            ),
            (
                "CATERING",
                "CATERING.CATERING_EVENT.CONFIRM",
            ),
            (
                "PROCUREMENT",
                "PROCUREMENT.PURCHASE_REQUEST.CREATE",
            ),
            (
                "PROCUREMENT",
                "PROCUREMENT.PURCHASE_ORDER.CREATE",
            ),
            (
                "PROCUREMENT",
                "PROCUREMENT.PURCHASE_REQUEST.SUBMIT",
            ),
            (
                "PROCUREMENT",
                "PROCUREMENT.PURCHASE_REQUEST.APPROVE",
            ),
            (
                "PROCUREMENT",
                "PROCUREMENT.PURCHASE_ORDER.SUBMIT",
            ),
            (
                "PROCUREMENT",
                "PROCUREMENT.PURCHASE_ORDER.APPROVE",
            ),
            (
                "PROCUREMENT",
                "PROCUREMENT.PURCHASE_ORDER.RECEIVE",
            ),
            (
                "CATERING",
                "CATERING.STOCK_MOVEMENT.CREATE",
            ),
            (
                "CATERING",
                "CATERING.STOCK_MOVEMENT.POST",
            ),
            (
                "EXPENSE",
                "EXPENSE.EXPENSE.APPROVE",
            ),
        ]

        for module_name, permission_name in required_permissions:
            permission = (
                db.session.query(Permission)
                .filter_by(name=permission_name.lower())
                .first()
            )

            if permission is None:
                permission = Permission(
                    name=permission_name.lower(),
                    module=module_name,
                    description=f"C6.8 E2E permission: {permission_name}",
                )
                db.session.add(permission)
                db.session.flush()

            existing_assignment = (
                db.session.query(RolePermission)
                .filter_by(
                    role_id=administrator_role.id,
                    permission_id=permission.id,
                )
                .first()
            )

            if existing_assignment is None:
                db.session.add(
                    RolePermission(
                        role=administrator_role,
                        permission=permission,
                    )
                )

        db.session.flush()

        # ------------------------------------------------------------------
        # 1. Customer -> Event -> Quotation -> Requirements
        # ------------------------------------------------------------------

        customer = Customer(
            name="C6.8 Full Pilot Customer",
            customer_type="ORGANIZATION",
            email="c6.8@example.test",
            phone="+211000000000",
        )
        db.session.add(customer)
        db.session.flush()

        request = CateringRequest(
            customer_id=customer.id,
            request_date=date(2026, 10, 1),
            requested_service="C6.8 Pilot Catering Service",
            service_date=date(2026, 10, 5),
            attendance=50,
            requirements="Full pilot acceptance scenario",
            notes="C6.8 end-to-end validation",
        )
        db.session.add(request)
        db.session.flush()

        event = CateringEvent(
            request_id=request.id,
            customer_id=customer.id,
            event_date=date(2026, 10, 5),
            service_details="C6.8 Full Pilot Catering Event",
            attendance=50,
            operational_notes="Full pilot acceptance scenario",
            status="REQUESTED",
        )
        db.session.add(event)
        db.session.flush()

        quotation = CateringQuotation(
            customer_id=customer.id,
            event_id=event.id,
            quotation_date=date(2026, 10, 1),
            valid_until=date(2026, 10, 4),
            subtotal=Decimal("1250.00"),
            adjustment_amount=Decimal("0.00"),
            total_amount=Decimal("1250.00"),
            status="ACCEPTED",
        )
        db.session.add(quotation)
        db.session.flush()

        event_requirement = EventRequirement(
            event_id=event.id,
            description="Food supplies for C6.8 pilot event",
            item_reference="FOOD-C6.8",
            quantity=Decimal("10"),
            unit="units",
            fulfilment_type="PROCUREMENT",
            required_by_date=date(2026, 10, 4),
            notes="C6.8 procurement requirement",
            status="IDENTIFIED",
        )
        db.session.add(event_requirement)
        db.session.flush()

        catering_purchase_requirement = CateringPurchaseRequirement(
            event_requirement_id=event_requirement.id,
            description="Food supplies for C6.8 pilot event",
            item_reference="FOOD-C6.8",
            quantity=Decimal("10"),
            unit="units",
            required_by_date=date(2026, 10, 4),
            justification="C6.8 pilot event procurement",
            status="DRAFT",
        )
        db.session.add(catering_purchase_requirement)
        db.session.flush()

        # The accepted quotation progresses the event through the existing
        # Catering quotation/event coordination boundary.
        catering_authorization_adapter = CateringAuthorizationAdapter(
            AuthorizationService.authorize_execution
        )

        quotation_event_coordination = (
            CateringQuotationEventCoordinationService(
                authorization_adapter=catering_authorization_adapter,
            )
        )

        event = (
            quotation_event_coordination.progress_event_from_accepted_quotation(
                quotation.id,
                subject=str(admin_user.id),
            )
        )

        assert event.status == "QUOTED"

        event_service = CateringEventService(
            authorization_adapter=catering_authorization_adapter,
        )

        event = event_service.request_confirmation(
            event,
            subject=str(admin_user.id),
        )
        assert event.status == "PENDING_CONFIRMATION"

        event = event_service.confirm(
            event,
            subject=str(admin_user.id),
        )
        assert event.status == "CONFIRMED"

        # ------------------------------------------------------------------
        # 2. Catering Purchase Requirement -> Procurement Requirement
        # ------------------------------------------------------------------

        handoff_service = CateringProcurementHandoffService(
            authorization_adapter=catering_authorization_adapter,
        )

        procurement_requirement = (
            handoff_service.submit_to_procurement(
                catering_purchase_requirement,
                subject=str(admin_user.id),
            )
        )

        assert procurement_requirement is not None
        assert (
            catering_purchase_requirement.procurement_reference
            == procurement_requirement.reference
        )

        # ------------------------------------------------------------------
        # 3. Procurement Requirement -> Purchase Request -> Purchase Order
        # ------------------------------------------------------------------

        supplier = Supplier(
            name="C6.8 Pilot Supplier",
            code="C6.8-SUP-001",
            supplier_type="CATERING_SUPPLIER",
            status="ACTIVE",
        )
        db.session.add(supplier)
        db.session.flush()

        purchase_flow_service = ProcurementPurchaseFlowService()

        procurement_context = ExecutionContext(
            user_id=str(admin_user.id),
            module_name="PROCUREMENT",
            operation="procurement.purchase_request.create",
        )

        purchase_request = (
            purchase_flow_service.create_purchase_request_from_requirement(
                procurement_requirement,
                reference="C6.8-PR-001",
                request_date=date(2026, 10, 1),
                required_by_date=date(2026, 10, 4),
                justification="C6.8 pilot event procurement",
                notes="C6.8 full pilot purchase request",
                subject=str(admin_user.id),
            )
        )

        assert isinstance(purchase_request, PurchaseRequest)
        assert purchase_request.status == "DRAFT"
        assert (
            purchase_request.purchase_requirement_id
            == procurement_requirement.id
        )

        purchase_request_service = PurchaseRequestService()

        submit_request_context = ExecutionContext(
            user_id=str(admin_user.id),
            module_name="PROCUREMENT",
            operation="procurement.purchase_request.submit",
        )
        purchase_request_service.submit(
            purchase_request
        )

        approve_request_context = ExecutionContext(
            user_id=str(admin_user.id),
            module_name="PROCUREMENT",
            operation="procurement.purchase_request.approve",
        )
        purchase_request_service.approve(
            purchase_request
        )

        db.session.flush()

        assert purchase_request.status == "APPROVED"

        purchase_order_context = ExecutionContext(
            user_id=str(admin_user.id),
            module_name="PROCUREMENT",
            operation="procurement.purchase_order.create",
        )

        purchase_order = (
            purchase_flow_service.create_purchase_order_from_request(
                purchase_request,
                reference="C6.8-PO-001",
                supplier_id=supplier.id,
                order_date=date(2026, 10, 1),
                expected_delivery_date=date(2026, 10, 4),
                subject=str(admin_user.id),
            )
        )

        assert isinstance(purchase_order, PurchaseOrder)
        assert purchase_order.status == "DRAFT"
        assert purchase_order.purchase_request_id == purchase_request.id

        purchase_order_service = PurchaseOrderService()

        submit_order_context = ExecutionContext(
            user_id=str(admin_user.id),
            module_name="PROCUREMENT",
            operation="procurement.purchase_order.submit",
        )
        purchase_order_service.submit(
            purchase_order
        )

        approve_order_context = ExecutionContext(
            user_id=str(admin_user.id),
            module_name="PROCUREMENT",
            operation="procurement.purchase_order.approve",
        )
        purchase_order_service.approve(
            purchase_order
        )

        db.session.flush()

        assert purchase_order.status == "APPROVED"

        # ------------------------------------------------------------------
        # 4. Approved PO -> Procurement Receiving -> Inventory
        # ------------------------------------------------------------------

        # Establish the minimum Inventory master data required by the
        # real Procurement -> Inventory receiving integration.
        product_category = ProductCategory(
            name="C6.8 Catering Supplies",
            code="C6.8-CAT-SUPPLIES",
            description="C6.8 pilot inventory supplies",
            is_active=True,
        )
        db.session.add(product_category)
        db.session.flush()

        product = Product(
            category_id=product_category.id,
            name="C6.8 Food Supplies",
            code="FOOD-C6.8",
            description="C6.8 pilot food supplies",
            unit="units",
            is_active=True,
        )
        db.session.add(product)
        db.session.flush()

        stock_item = StockItem(
            product_id=product.id,
            minimum_level=Decimal("0"),
            reorder_level=Decimal("0"),
            is_active=True,
        )
        db.session.add(stock_item)

        inventory_location = InventoryLocation(
            code="MAIN",
            name="C6.8 Main Store",
            description="C6.8 pilot receiving location",
            is_active=True,
        )
        db.session.add(inventory_location)
        db.session.flush()

        receive_context = ExecutionContext(
            user_id=str(admin_user.id),
            module_name="PROCUREMENT",
            operation="procurement.purchase_order.receive",
        )

        receive_result = app.extensions["command_dispatcher"].dispatch(
            ReceivePurchaseOrderCommand(
                purchase_order_id=purchase_order.id,
                purchase_order_reference=purchase_order.reference,
                purchase_order_line_reference="C6.8-PO-001-LINE-001",
                stock_item_reference="FOOD-C6.8",
                inventory_location_reference="MAIN",
                quantity_received=Decimal("10"),
                unit="units",
                received_at=datetime.now(timezone.utc),
                receiving_reference="C6.8-GRN-001",
                idempotency_key="C6.8-PO-001-RECEIPT-001",
                notes="C6.8 pilot receipt",
            ),
            receive_context,
        )

        assert receive_result.is_success()

        db.session.expire_all()

        persisted_purchase_order = db.session.get(
            PurchaseOrder,
            purchase_order.id,
        )
        assert persisted_purchase_order.status == "APPROVED"

        # ------------------------------------------------------------------
        # 5. Production / Delivery -> final Catering event state
        # ------------------------------------------------------------------

        # C6.5 established that Production / Delivery is represented by the
        # Catering Event lifecycle, but the current application exposes no
        # dedicated service operations for these later states. Establish the
        # final event state as a fixture boundary rather than introducing new
        # application functionality solely for C6.8.
        persisted_event = db.session.get(CateringEvent, event.id)
        persisted_event.status = "COMPLETED"
        db.session.flush()

        # ------------------------------------------------------------------
        # 6. Revenue -> Finance
        # ------------------------------------------------------------------

        revenue = CateringRevenue(
            revenue_reference="CAT-REV-C6.8-001",
            source_type="CATERING_EVENT",
            source_reference=f"EVENT-{event.id}",
            customer_id=customer.id,
            event_id=event.id,
            amount=Decimal("1250.00"),
            currency="USD",
            revenue_date=date(2026, 10, 5),
            revenue_classification="CATERING_SERVICE",
            status=CateringRevenueWorkflow.DRAFT,
        )
        db.session.add(revenue)
        db.session.flush()

        revenue.status = CateringRevenueWorkflow.ELIGIBLE

        # ------------------------------------------------------------------
        # 7. Submitted Expense -> Approved Expense -> Catering Cost
        # ------------------------------------------------------------------

        classification = ExpenseClassification(
            code="CATERING-OPERATIONS-C6.8",
            name="C6.8 Catering Operations",
            description="C6.8 pilot catering operating costs",
        )
        db.session.add(classification)
        db.session.flush()

        expense = Expense(
            classification_id=classification.id,
            description="C6.8 pilot food supplies",
            amount=Decimal("150.00"),
            expense_date=date(2026, 10, 4),
            status=SUBMITTED,
        )
        db.session.add(expense)
        db.session.flush()

        association = CateringExpenseCostAssociation(
            expense_id=expense.id,
            catering_context_type="CATERING_EVENT",
            catering_context_reference=f"EVENT-{event.id}",
            status="ELIGIBLE",
            contribution_id="C6.8-COST-001",
        )
        db.session.add(association)
        db.session.flush()

        db.session.commit()

        revenue_id = revenue.id
        revenue_reference = revenue.revenue_reference
        expense_id = expense.id
        association_id = association.id

        # ------------------------------------------------------------------
        # 8. Execute the two post-commit integration paths
        # ------------------------------------------------------------------

        revenue_context = ExecutionContext(
            user_id=str(admin_user.id),
            module_name="CATERING",
            operation="catering.revenue.recognize",
        )

        revenue_result = app.extensions["command_dispatcher"].dispatch(
            RecognizeCateringRevenueCommand(
                revenue_id=revenue_id,
            ),
            revenue_context,
        )

        assert revenue_result.is_success()

        expense_approval_context = ExecutionContext(
            user_id=str(admin_user.id),
            module_name="EXPENSE",
            operation="expense.approve",
        )

        expense_result = app.extensions["command_dispatcher"].dispatch(
            ApproveExpenseCommand(expense_id=expense_id),
            expense_approval_context,
        )

        assert expense_result.is_success()

        db.session.expire_all()

        # ------------------------------------------------------------------
        # 9. Final profitability validation
        # ------------------------------------------------------------------

        persisted_revenue = db.session.get(
            CateringRevenue,
            revenue_id,
        )
        assert persisted_revenue.status == CateringRevenueWorkflow.RECOGNIZED
        assert persisted_revenue.revenue_reference == revenue_reference

        finance_revenues = (
            db.session.query(FinanceRevenue)
            .filter_by(contribution_reference=revenue_reference)
            .all()
        )
        assert len(finance_revenues) == 1
        assert finance_revenues[0].status == "PENDING"

        persisted_expense = db.session.get(
            Expense,
            expense_id,
        )
        assert persisted_expense.status == APPROVED

        persisted_association = db.session.get(
            CateringExpenseCostAssociation,
            association_id,
        )
        assert persisted_association.status == "CONSUMED"

        profitability_service = EventProfitabilityService(
            catering_event_repository=CateringEventRepository(),
            catering_revenue_repository=CateringRevenueRepository(),
            expense_cost_association_repository=(
                CateringExpenseCostAssociationRepository()
            ),
            expense_repository=ExpenseRepository(),
        )

        result = profitability_service.calculate_for_event(event.id)

        assert result.event_id == event.id
        assert result.event_reference == f"EVENT-{event.id}"
        assert result.revenue_amount == Decimal("1250.00")
        assert result.total_cost == Decimal("150.00")
        assert result.profit == Decimal("1100.00")
        assert len(result.cost_contributions) == 1
        assert result.cost_contributions[0].expense_id == expense_id
        assert result.cost_contributions[0].association_id == association_id
