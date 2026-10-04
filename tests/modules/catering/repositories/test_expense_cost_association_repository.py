from unittest.mock import Mock, patch

from app.core.data.sqlalchemy_repository import SQLAlchemyRepository
from app.modules.catering.models import CateringExpenseCostAssociation
from app.modules.catering.repositories import (
    CateringExpenseCostAssociationRepository,
)


def test_repository_binds_to_expected_model():
    repository = CateringExpenseCostAssociationRepository()

    assert isinstance(repository, SQLAlchemyRepository)
    assert repository.model is CateringExpenseCostAssociation


def test_repository_uses_sqlalchemy_repository_contract():
    repository = CateringExpenseCostAssociationRepository()

    assert isinstance(repository, SQLAlchemyRepository)


def test_repository_model_reference_is_stable():
    repository = CateringExpenseCostAssociationRepository()

    assert repository.model.__tablename__ == (
        "catering_expense_cost_associations"
    )


def test_get_eligible_by_expense_id_queries_eligible_associations():
    repository = CateringExpenseCostAssociationRepository()

    eligible_association = Mock(
        spec=CateringExpenseCostAssociation,
    )

    session = Mock()
    session.execute.return_value.scalars.return_value.all.return_value = [
        eligible_association
    ]

    with patch(
        "app.modules.catering.repositories.expense_cost_association.db.session",
        session,
    ):
        result = repository.get_eligible_by_expense_id(17)

    assert result == [eligible_association]
    session.execute.assert_called_once()


def test_get_by_contribution_id_queries_stable_contribution_identity():
    repository = CateringExpenseCostAssociationRepository()

    association = Mock(
        spec=CateringExpenseCostAssociation,
    )

    session = Mock()
    session.execute.return_value.scalar_one_or_none.return_value = association

    with patch(
        "app.modules.catering.repositories.expense_cost_association.db.session",
        session,
    ):
        result = repository.get_by_contribution_id(
            "expense-17-catering-event-1"
        )

    assert result is association
    session.execute.assert_called_once()

    statement = session.execute.call_args.args[0]
    compiled = statement.compile(
        compile_kwargs={"literal_binds": True}
    )

    assert "contribution_id" in str(compiled)
    assert "expense-17-catering-event-1" in str(compiled)


def test_get_consumed_by_catering_context_queries_consumed_associations():
    repository = CateringExpenseCostAssociationRepository()

    consumed_association = Mock(
        spec=CateringExpenseCostAssociation,
    )

    session = Mock()
    session.execute.return_value.scalars.return_value.all.return_value = [
        consumed_association
    ]

    with patch(
        "app.modules.catering.repositories.expense_cost_association.db.session",
        session,
    ):
        result = repository.get_consumed_by_catering_context(
            "CATERING_EVENT",
            "EVENT-42",
        )

    assert result == [consumed_association]
    session.execute.assert_called_once()

    statement = session.execute.call_args.args[0]
    compiled = statement.compile(
        compile_kwargs={"literal_binds": True}
    )

    compiled_sql = str(compiled)

    assert "catering_context_type" in compiled_sql
    assert "CATERING_EVENT" in compiled_sql
    assert "catering_context_reference" in compiled_sql
    assert "EVENT-42" in compiled_sql
    assert "status" in compiled_sql
    assert "CONSUMED" in compiled_sql
