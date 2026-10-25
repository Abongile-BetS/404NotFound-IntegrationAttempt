from fastapi import APIRouter

from app.modules.screening.application.screening_service import ScreeningService
from app.modules.screening.schemas.screening_response import ScreeningResponse

router = APIRouter(prefix="/screening", tags=["Screening"])

service = ScreeningService()


@router.get("", response_model=list[ScreeningResponse])
async def list_screening_results():
    return await service.list_screening_results()


@router.get("/dashboard")
async def get_screening_dashboard():
    return await service.get_dashboard()


@router.get("/workspace")
async def get_screening_workspace():
    return await service.get_workspace_dashboard()


@router.get("/{customer_id}", response_model=list[ScreeningResponse])
async def get_screening(customer_id: str):
    return await service.get_customer_screening(customer_id)