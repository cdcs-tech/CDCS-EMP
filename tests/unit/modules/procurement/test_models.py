"""
Procurement domain model foundation tests.
"""

from sqlalchemy import inspect

from app.extensions import db
from app.models.base import BaseModel
from app.models.mixins import (
    AuditMixin,
    SoftDeleteMixin,
    TimestampMixin,
)

from app.modules.procurement.models import (
    PurchaseOrder,
    PurchaseOrderLine,
    PurchaseRequest,
    PurchaseRequestLine,
    PurchaseRequirement,
    Supplier,
)


PROCUREMENT_MODELS = (
    Supplier,
    PurchaseRequirement,
    PurchaseRequest,
    PurchaseRequestLine,
    PurchaseOrder,
    PurchaseOrderLine,
)


def test_procurement_models_use_enterprise_model_foundation():
    """
    All Procurement domain models must use the standard
    enterprise model foundation and governance mixins.
    """

    for model in PROCUREMENT_MODELS:
        assert issubclass(model, BaseModel)
        assert issubclass(model, TimestampMixin)
        assert issubclass(model, AuditMixin)
        assert issubclass(model, SoftDeleteMixin)


def test_procurement_models_have_expected_table_names():
    """
    Procurement model table names must remain explicit and
    module-specific.
    """

    assert Supplier.__tablename__ == "suppliers"
    assert (
        PurchaseRequirement.__tablename__
        == "purchase_requirements"
    )
    assert PurchaseRequest.__tablename__ == "purchase_requests"
    assert (
        PurchaseRequestLine.__tablename__
        == "purchase_request_lines"
    )
    assert PurchaseOrder.__tablename__ == "purchase_orders"
    assert (
        PurchaseOrderLine.__tablename__
        == "purchase_order_lines"
    )


def test_procurement_models_are_registered_in_sqlalchemy_metadata(
    app,
):
    """
    The six Procurement models must be attached to the existing
    SQLAlchemy metadata when the Procurement module registers
    its models.
    """

    module = __import__(
        "app.modules.procurement",
        fromlist=["ProcurementModule"],
    ).ProcurementModule()

    module.register_models(app)

    expected_tables = {
        "suppliers",
        "purchase_requirements",
        "purchase_requests",
        "purchase_request_lines",
        "purchase_orders",
        "purchase_order_lines",
    }

    assert expected_tables.issubset(
        set(db.metadata.tables.keys())
    )


def test_purchase_request_relationships_are_internal_to_procurement():
    """
    PurchaseRequest relationships must use Procurement-owned
    entities only.
    """

    request_mapper = inspect(PurchaseRequest)

    assert "purchase_requirement" in request_mapper.relationships
    assert "lines" in request_mapper.relationships
    assert "purchase_orders" in request_mapper.relationships

    assert (
        request_mapper.relationships[
            "purchase_requirement"
        ].mapper.class_
        is PurchaseRequirement
    )

    assert (
        request_mapper.relationships["lines"].mapper.class_
        is PurchaseRequestLine
    )

    assert (
        request_mapper.relationships[
            "purchase_orders"
        ].mapper.class_
        is PurchaseOrder
    )


def test_purchase_order_relationships_are_internal_to_procurement():
    """
    PurchaseOrder relationships must use Procurement-owned
    entities only.
    """

    order_mapper = inspect(PurchaseOrder)

    assert "supplier" in order_mapper.relationships
    assert "purchase_request" in order_mapper.relationships
    assert "lines" in order_mapper.relationships

    assert (
        order_mapper.relationships["supplier"].mapper.class_
        is Supplier
    )

    assert (
        order_mapper.relationships[
            "purchase_request"
        ].mapper.class_
        is PurchaseRequest
    )

    assert (
        order_mapper.relationships["lines"].mapper.class_
        is PurchaseOrderLine
    )


def test_purchase_requirement_relationships_are_internal_to_procurement():
    """
    PurchaseRequirement must relate only to Procurement-owned
    PurchaseRequest entities.
    """

    mapper = inspect(PurchaseRequirement)

    assert "purchase_requests" in mapper.relationships

    assert (
        mapper.relationships[
            "purchase_requests"
        ].mapper.class_
        is PurchaseRequest
    )


def test_supplier_relationships_are_internal_to_procurement():
    """
    Supplier must relate only to Procurement-owned
    PurchaseOrder entities.
    """

    mapper = inspect(Supplier)

    assert "purchase_orders" in mapper.relationships

    assert (
        mapper.relationships[
            "purchase_orders"
        ].mapper.class_
        is PurchaseOrder
    )


def test_purchase_request_line_relationship_is_internal_to_procurement():
    """
    PurchaseRequestLine must relate to its Procurement-owned
    PurchaseRequest parent.
    """

    mapper = inspect(PurchaseRequestLine)

    assert "purchase_request" in mapper.relationships

    assert (
        mapper.relationships[
            "purchase_request"
        ].mapper.class_
        is PurchaseRequest
    )


def test_purchase_order_line_relationship_is_internal_to_procurement():
    """
    PurchaseOrderLine must relate to its Procurement-owned
    PurchaseOrder parent.
    """

    mapper = inspect(PurchaseOrderLine)

    assert "purchase_order" in mapper.relationships

    assert (
        mapper.relationships[
            "purchase_order"
        ].mapper.class_
        is PurchaseOrder
    )


def test_procurement_models_have_no_external_business_module_foreign_keys():
    """
    Procurement Foundation must not introduce direct foreign
    keys to Catering, Inventory, Finance, or other external
    business-module entities.
    """

    external_table_prefixes = (
        "catering_",
        "product",
        "stock_",
        "inventory_",
        "expense",
        "finance_",
        "accounting_",
    )

    for model in PROCUREMENT_MODELS:
        for column in model.__table__.columns:
            for foreign_key in column.foreign_keys:
                target_table = foreign_key.target_fullname.split(
                    "."
                )[0]

                assert not target_table.startswith(
                    external_table_prefixes
                )
