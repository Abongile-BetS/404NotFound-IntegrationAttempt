from pydantic import BaseModel


class ScreeningResponse(BaseModel):
    id: str
    customer: str
    customerId: str
    source: str | None
    status: str | None
    score: str | None
    time: str | None