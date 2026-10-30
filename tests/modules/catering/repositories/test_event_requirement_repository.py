from unittest.mock import Mock, patch

from sqlalchemy.dialects import mssql

from app.modules.catering.models import EventRequirement
from app.modules.catering.repositories import EventRequirementRepository


def test_get_by_id_for_update_uses_sql_server_compatible_soft_delete_filter():
    repository = EventRequirementRepository()
    requirement = Mock(spec=EventRequirement)

    session = Mock()
    session.execute.return_value.scalar_one_or_none.return_value = requirement

    with patch(
        "app.modules.catering.repositories.event_requirement.db.session",
        session,
    ):
        result = repository.get_by_id_for_update(10)

    assert result is requirement
    session.execute.assert_called_once()

    statement = session.execute.call_args.args[0]
    compiled_sql = str(statement.compile(dialect=mssql.dialect()))

    assert "WITH (UPDLOCK, HOLDLOCK)" in compiled_sql
    normalized_sql = compiled_sql.replace("[", "").replace("]", "")

    assert "is_deleted = 0" in normalized_sql
    assert "is_deleted IS 0" not in normalized_sql
