from fastapi import APIRouter

from app.modules.network_intelligence.application.network_intelligence_service import NetworkIntelligenceService

router = APIRouter(prefix="/network", tags=["Network Intelligence"])
service = NetworkIntelligenceService()


@router.get("/dashboard")
async def get_network_workspace():
    return await service.get_workspace_dashboard()