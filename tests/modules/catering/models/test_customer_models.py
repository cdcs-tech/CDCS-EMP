"""
CDCS Enterprise Management Platform (CDCS-EMP)

Catering Module

Focused tests for the Customer model.
"""

from datetime import datetime

from app.modules.catering.models import Customer


def test_customer_has_expected_table_and_columns():
    assert Customer.__tablename__ == "customers"

    assert Customer.id is not None
    assert Customer.guid is not None

    assert Customer.name.property.columns[0].nullable is False
    assert Customer.customer_type.property.columns[0].nullable is False
    assert Customer.phone.property.columns[0].nullable is True
    assert Customer.email.property.columns[0].nullable is True
    assert Customer.address.property.columns[0].nullable is True
    assert Customer.notes.property.columns[0].nullable is True
    assert Customer.status.property.columns[0].nullable is False


def test_customer_has_expected_field_lengths():
    assert Customer.name.property.columns[0].type.length == 150
    assert Customer.customer_type.property.columns[0].type.length == 50
    assert Customer.phone.property.columns[0].type.length == 50
    assert Customer.email.property.columns[0].type.length == 150
    assert Customer.address.property.columns[0].type.length == 500
    assert Customer.notes.property.columns[0].type.length == 1000
    assert Customer.status.property.columns[0].type.length == 20


def test_customer_has_expected_controlled_value_constraints():
    constraints = {
        constraint.name: str(constraint.sqltext)
        for constraint in Customer.__table__.constraints
        if constraint.name
        in {
            "ck_customers_customer_type",
            "ck_customers_status",
        }
    }

    assert "ck_customers_customer_type" in constraints
    assert "INDIVIDUAL" in constraints["ck_customers_customer_type"]
    assert "ORGANIZATION" in constraints["ck_customers_customer_type"]

    assert "ck_customers_status" in constraints
    assert "ACTIVE" in constraints["ck_customers_status"]
    assert "INACTIVE" in constraints["ck_customers_status"]


def test_customer_inherits_enterprise_mixins():
    customer = Customer(
        name="Example Customer",
        customer_type="INDIVIDUAL",
    )

    assert hasattr(customer, "created_at")
    assert hasattr(customer, "updated_at")
    assert hasattr(customer, "created_by")
    assert hasattr(customer, "updated_by")

    assert Customer.is_deleted.property.columns[0].default.arg is False


def test_customer_has_expected_default_status():
    status_column = Customer.status.property.columns[0]

    assert status_column.default.arg == "ACTIVE"


def test_customer_accepts_individual_type():
    customer = Customer(
        name="John Doe",
        customer_type="INDIVIDUAL",
    )

    assert customer.name == "John Doe"
    assert customer.customer_type == "INDIVIDUAL"


def test_customer_accepts_organization_type():
    customer = Customer(
        name="Example Organization",
        customer_type="ORGANIZATION",
    )

    assert customer.name == "Example Organization"
    assert customer.customer_type == "ORGANIZATION"


def test_customer_soft_delete_methods_work():
    customer = Customer(
        name="Example Customer",
        customer_type="INDIVIDUAL",
    )

    customer.soft_delete()

    assert customer.is_deleted is True
    assert isinstance(
        customer.deleted_at,
        datetime,
    )

    customer.restore()

    assert customer.is_deleted is False
    assert customer.deleted_at is None
