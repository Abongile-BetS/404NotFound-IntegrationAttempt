from app.modules.risk_scoring.infrastructure.risk_scoring_repository import (
    RiskScoringRepository,
)


class RiskScoringService:

    def __init__(self):
        self.repository = RiskScoringRepository()

    async def get_customer_risk_score(self, customer_id: str):
        return await self.repository.get_by_customer_id(customer_id)