from fastapi import APIRouter

from app.modules.transaction_monitoring.application.transaction_monitoring_service import TransactionMonitoringService
from app.modules.transaction_monitoring.schemas.transaction_response import TransactionResponse


router = APIRouter(prefix="/transactions", tags=["Transaction Monitoring"])
service = TransactionMonitoringService()


@router.get("", response_model=list[TransactionResponse])
async def list_transactions():
    return await service.list_transactions()


@router.get("/dashboard")
async def get_transaction_workspace():
    return await service.get_workspace_dashboard()