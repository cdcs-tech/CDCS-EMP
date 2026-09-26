from app.modules.procurement.models import (
    ProcurementFinanceCommitment,
)


def test_finance_commitment_has_expected_table_name():
    assert (
        ProcurementFinanceCommitment.__tablename__
        == "procurement_finance_commitments"
    )


def test_finance_commitment_has_expected_columns():
    columns = ProcurementFinanceCommitment.__table__.columns

    expected = {
        "purchase_order_id",
        "purchase_order_reference",
        "idempotency_key",
        "status",
        "attempt_count",
        "last_attempted_at",
        "committed_at",
        "last_failure_at",
        "next_retry_at",
        "last_error",
        "last_response_message",
        "last_response_status_code",
    }

    assert expected.issubset(columns.keys())


def test_finance_commitment_has_expected_identity_constraints():
    table = ProcurementFinanceCommitment.__table__

    assert table.c.purchase_order_id.unique is True
    assert table.c.idempotency_key.unique is True
    assert table.c.purchase_order_id.nullable is False
    assert table.c.purchase_order_reference.nullable is False
    assert table.c.idempotency_key.nullable is False


def test_finance_commitment_has_expected_initial_defaults():
    table = ProcurementFinanceCommitment.__table__

    assert table.c.status.default.arg == "PENDING"
    assert table.c.attempt_count.default.arg == 0


def test_finance_commitment_has_purchase_order_foreign_key():
    table = ProcurementFinanceCommitment.__table__

    foreign_keys = {
        (
            foreign_key.parent.name,
            foreign_key.target_fullname,
        )
        for foreign_key in table.foreign_keys
    }

    assert (
        "purchase_order_id",
        "purchase_orders.id",
    ) in foreign_keys


def test_finance_commitment_retry_timestamps_are_nullable():
    table = ProcurementFinanceCommitment.__table__

    for column_name in (
        "last_attempted_at",
        "committed_at",
        "last_failure_at",
        "next_retry_at",
    ):
        assert table.c[column_name].nullable is True


def test_finance_commitment_response_fields_are_nullable():
    table = ProcurementFinanceCommitment.__table__

    for column_name in (
        "last_error",
        "last_response_message",
        "last_response_status_code",
    ):
        assert table.c[column_name].nullable is True
