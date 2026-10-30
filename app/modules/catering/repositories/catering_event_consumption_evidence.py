"""Repository for Catering Event physical-consumption evidence."""

from __future__ import annotations

from sqlalchemy import false, select

from app.core.data.sqlalchemy_repository import SQLAlchemyRepository
from app.extensions import db
from app.modules.catering.models import CateringEventConsumptionEvidence


class CateringEventConsumptionEvidenceRepository(
    SQLAlchemyRepository[CateringEventConsumptionEvidence],
):
    """Persist and retrieve physical-consumption evidence."""

    def __init__(self) -> None:
        super().__init__(CateringEventConsumptionEvidence)

    def get_by_requirement_id(
        self,
        requirement_id: int,
    ) -> list[CateringEventConsumptionEvidence]:
        """Return active evidence records for one Event Requirement."""
        statement = (
            select(CateringEventConsumptionEvidence)
            .where(
                CateringEventConsumptionEvidence.event_requirement_id
                == requirement_id,
                CateringEventConsumptionEvidence.is_deleted == false(),
            )
        )
        return list(db.session.execute(statement).scalars().all())

    def get_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> CateringEventConsumptionEvidence | None:
        """Return evidence associated with an idempotency key."""
        statement = select(CateringEventConsumptionEvidence).where(
            CateringEventConsumptionEvidence.idempotency_key
            == idempotency_key,
        )
        return db.session.execute(statement).scalar_one_or_none()


__all__ = ["CateringEventConsumptionEvidenceRepository"]
