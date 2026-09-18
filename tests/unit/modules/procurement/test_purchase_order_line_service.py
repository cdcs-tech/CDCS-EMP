from app.modules.procurement.models import PurchaseOrderLine
from app.modules.procurement.repositories import (
    PurchaseOrderLineRepository,
)
from app.modules.procurement.services import (
    PurchaseOrderLineService,
)


def test_purchase_order_line_service_uses_purchase_order_line_repository():
    service = PurchaseOrderLineService()

    assert isinstance(
        service.repository,
        PurchaseOrderLineRepository,
    )
    assert service.repository.model is PurchaseOrderLine


def test_purchase_order_line_service_accepts_injected_repository():
    repository = PurchaseOrderLineRepository()
    service = PurchaseOrderLineService(
        repository=repository,
    )

    assert service.repository is repository


def test_purchase_order_line_service_exposes_crud_operations():
    service = PurchaseOrderLineService()

    assert callable(service.create)
    assert callable(service.get)
    assert callable(service.update)
    assert callable(service.delete)
