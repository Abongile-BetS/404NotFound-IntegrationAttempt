from pydantic import BaseModel


class RiskEventResponse(BaseModel):
    risk_category: str | None
    risk_type: str
    contribution: float | None
    description: str | None
    severity: str
    status: str
    detected_at: str