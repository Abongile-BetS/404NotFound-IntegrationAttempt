from fastapi import APIRouter, HTTPException

from app.modules.risk_scoring.application.risk_scoring_service import RiskScoringService
from app.modules.risk_scoring.schemas.risk_score_response import RiskScoreResponse


router = APIRouter(prefix="/risk-scoring", tags=["Risk Scoring"])
service = RiskScoringService()


@router.get("/customers/{customer_id}", response_model=RiskScoreResponse)
async def get_customer_risk_score(customer_id: str):
	score = await service.get_customer_risk_score(customer_id)
	if score is None:
		raise HTTPException(status_code=404, detail="Risk score not found")
	return score
