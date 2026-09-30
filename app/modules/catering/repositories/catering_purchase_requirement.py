from app.core.data.sqlalchemy_repository import (
    SQLAlchemyRepository,
)

from app.modules.catering.models.catering_purchase_requirement import (
    CateringPurchaseRequirement,
)


class CateringPurchaseRequirementRepository(
    SQLAlchemyRepository[CateringPurchaseRequirement]
):
    def __init__(self):
        super().__init__(CateringPurchaseRequirement)
