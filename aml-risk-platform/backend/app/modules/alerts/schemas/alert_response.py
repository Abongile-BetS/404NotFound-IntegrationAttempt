from pydantic import BaseModel


class AlertResponse(BaseModel):
    alert_id: str
    customer_id: str
    alert_type: str | None
    severity: str | None
    status: str | None
    created_at: str | None