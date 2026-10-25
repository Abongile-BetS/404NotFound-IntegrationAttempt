from fastapi import APIRouter

from app.modules.investigations.application.investigations_service import InvestigationsService
from app.modules.investigations.schemas.investigation_response import InvestigationResponse


router = APIRouter(prefix="/investigations", tags=["Investigations"])
service = InvestigationsService()


@router.get("", response_model=list[InvestigationResponse])
async def list_investigations():
    return await service.list_cases()


@router.get("/dashboard")
async def get_investigation_workspace():
    return await service.get_workspace_dashboard()