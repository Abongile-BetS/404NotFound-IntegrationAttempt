from fastapi import APIRouter, HTTPException

from app.modules.investigations.application.investigations_service import (
    InvestigationsService,
)

router = APIRouter(prefix="/investigations", tags=["Investigations"])
service = InvestigationsService()


@router.get("/dashboard")
async def get_investigation_workspace():
    from app.modules.workspace.api.workspace_router import get_workspace_data

    return await get_workspace_data("investigations")


@router.get("")
async def list_investigations():
    return await service.list_cases()


@router.post("")
async def create_investigation(payload: dict):
    title = payload.get("title")
    if not title:
        raise HTTPException(status_code=422, detail="title is required")
    return await service.create_case(
        title=title,
        customer_id=payload.get("customer_id"),
        alert_id=payload.get("alert_id"),
        priority=payload.get("priority"),
        assigned_to=payload.get("assigned_to"),
        notes=payload.get("notes"),
    )


@router.get("/{case_id}")
async def get_investigation(case_id: int):
    case = await service.get_case(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return case


@router.patch("/{case_id}")
async def update_investigation(case_id: int, payload: dict):
    case = await service.update_case(case_id, payload)
    if case is None:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return case
