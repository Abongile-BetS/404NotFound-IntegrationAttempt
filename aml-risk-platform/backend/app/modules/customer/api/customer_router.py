from fastapi import APIRouter, HTTPException

from app.modules.customer.application.customer_service import CustomerService
from app.modules.customer.schemas.customer_response import CustomerResponse


router = APIRouter(prefix="/customers", tags=["Customers"])
service = CustomerService()


@router.get("", response_model=list[CustomerResponse])
async def list_customers():
    return await service.list_customers()


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: str):
    customer = await service.get_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer