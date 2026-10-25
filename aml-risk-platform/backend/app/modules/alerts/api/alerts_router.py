from fastapi import APIRouter

from app.modules.alerts.application.alerts_service import AlertsService
from app.modules.alerts.schemas.alert_response import AlertResponse


router = APIRouter(prefix="/alerts", tags=["Alerts"])
service = AlertsService()


@router.get("", response_model=list[AlertResponse])
async def list_alerts():
    return await service.list_alerts()


@router.get("/dashboard")
async def get_alert_workspace():
    return await service.get_workspace_dashboard()