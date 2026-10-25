from pydantic import BaseModel

from app.modules.risk_scoring.schemas.risk_event_response import RiskEventResponse


class RiskScoreResponse(BaseModel):
    customer_id: str
    score: float | None
    risk_level: str | None
    scoring_method: str | None
    model_version: str | None
    calculated_at: str | None
    risk_events: list[RiskEventResponse]