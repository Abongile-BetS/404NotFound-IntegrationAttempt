from fastapi import APIRouter

from app.modules.reporting.application.reporting_service import ReportingService


router = APIRouter(tags=["Reporting"])
service = ReportingService()


@router.get("/dashboard")
async def get_dashboard():
    return await service.get_dashboard()


@router.get("/reporting/summary")
async def get_reporting_summary():
    return await service.get_summary()


@router.get("/reporting/dashboard")
async def get_home_workspace():
    return await service.get_home_workspace()


@router.get("/reporting/executive/dashboard")
async def get_executive_workspace():
    return await service.get_executive_workspace()