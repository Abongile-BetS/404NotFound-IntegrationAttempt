from pydantic import BaseModel


class CreateKycRequest(BaseModel):
    identity_status: str
    address_status: str
    verification_result: str