from pydantic import BaseModel


class KycResponse(BaseModel):
    customer_id: str
    identity_status: str | None
    address_status: str | None
    verification_result: str | None