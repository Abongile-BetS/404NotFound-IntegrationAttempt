from fastapi import APIRouter, HTTPException

from app.modules.screening.application.screening_service import ScreeningService
from app.modules.screening.schemas.screening_response import ScreeningResponse
from app.shared.pagination import PageLimit, PageOffset

router = APIRouter(prefix="/screening", tags=["Screening"])

service = ScreeningService()


@router.get("", response_model=list[ScreeningResponse])
async def list_screening_results(limit: PageLimit = 100, offset: PageOffset = 0):
    return await service.list_screening_results(limit=limit, offset=offset)


@router.get("/dashboard")
async def get_screening_dashboard(
    limit: PageLimit = 100,
    offset: PageOffset = 0,
):
    return await service.get_dashboard(limit=limit, offset=offset)


@router.get("/workspace")
async def get_screening_workspace():
    return await service.get_workspace_dashboard()


@router.get("/{customer_id}", response_model=list[ScreeningResponse])
async def get_screening(
    customer_id: str,
    limit: PageLimit = 100,
    offset: PageOffset = 0,
):
    return await service.get_customer_screening(
        customer_id,
        limit=limit,
        offset=offset,
    )


@router.patch("/{screening_id}")
async def update_screening_result(screening_id: str, payload: dict):
    result = await service.update_result(
        screening_id,
        result=payload.get("result"),
        match_found=payload.get("match_found"),
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Screening result not found")
    return result
