from fastapi import APIRouter, HTTPException

from app.modules.kyc.application.kyc_service import KycService
from app.modules.kyc.schemas.kyc_response import KycResponse
from app.shared.pagination import PageLimit, PageOffset

router = APIRouter(prefix="/kyc", tags=["KYC"])

service = KycService()


@router.get("", response_model=list[KycResponse])
async def list_kyc_records(limit: PageLimit = 100, offset: PageOffset = 0):
    return await service.list_records(limit=limit, offset=offset)


@router.get("/dashboard")
async def get_kyc_workspace():
    return await service.get_workspace_dashboard()


@router.get("/{customer_id}", response_model=KycResponse)
async def get_kyc(customer_id: str):
    record = await service.get_customer_kyc(customer_id)
    if record is None:
        raise HTTPException(status_code=404, detail="KYC record not found")
    return record
