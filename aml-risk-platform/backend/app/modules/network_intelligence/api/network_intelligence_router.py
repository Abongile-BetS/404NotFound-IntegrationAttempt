from fastapi import APIRouter, HTTPException

from app.modules.network_intelligence.application.network_intelligence_service import (
    NetworkIntelligenceService,
)
from app.shared.database.connection import fetch_all

router = APIRouter(prefix="/network", tags=["Network Intelligence"])
service = NetworkIntelligenceService()


@router.get("/dashboard")
async def get_network_workspace():
    return await service.get_workspace_dashboard()


@router.get("/customers/{customer_id}/relationships")
async def get_customer_relationships(customer_id: str, depth: int = 2):
    if depth < 1 or depth > 4:
        raise HTTPException(status_code=422, detail="depth must be between 1 and 4")

    rows = await fetch_all(
        """
        WITH RECURSIVE related AS (
            SELECT
                c.id AS customer_id,
                c.customer_guid::text AS customer_guid,
                0 AS hop
            FROM public.customer AS c
            WHERE c.customer_guid::text = :customer_id
            UNION
            SELECT
                peer.fk_customer_id,
                pc.customer_guid::text,
                r.hop + 1
            FROM related AS r
            JOIN network.customer_device AS cd ON cd.fk_customer_id = r.customer_id
            JOIN network.customer_device AS peer ON peer.fk_device_id = cd.fk_device_id
                AND peer.fk_customer_id <> r.customer_id
            JOIN public.customer AS pc ON pc.id = peer.fk_customer_id
            WHERE r.hop < :depth
        )
        SELECT
            customer_guid AS customer_id,
            MIN(hop) AS hops
        FROM related
        GROUP BY customer_guid
        ORDER BY hops, customer_guid
        """,
        {"customer_id": customer_id, "depth": depth},
    )
    return {"customer_id": customer_id, "depth": depth, "relationships": rows}
