from pydantic import BaseModel


class InvestigationResponse(BaseModel):
    case_id: str
    customer_id: str
    alert_id: str
    status: str
    priority: str
    outcome: str | None = None
    opened_at: str