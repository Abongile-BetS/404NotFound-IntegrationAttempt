from pydantic import BaseModel


class CustomerResponse(BaseModel):
    customer_id: str
    first_name: str
    last_name: str
    email: str | None
    country: str | None
    customer_status: str
    customer_type: str | None
    created_at: str