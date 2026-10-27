from app.modules.workspace.api.workspace_router import get_workspace_data
from app.shared.database.connection import fetch_all


class AlertsService:
    async def get_workspace_dashboard(self):
        return await get_workspace_data("alerts")

    async def list_alerts(self, limit: int = 100, offset: int = 0):
        return await fetch_all(
            """
            SELECT
                a.alert_guid::text AS alert_id,
                c.customer_guid::text AS customer_id,
                a.alert_type,
                a.severity,
                a.status,
                a.created_at::text AS created_at
            FROM public.alert AS a
            JOIN public.customer AS c ON c.id = a.fk_customer_id
            ORDER BY a.created_at DESC NULLS LAST, a.id DESC
            LIMIT :limit OFFSET :offset
            """,
            {"limit": limit, "offset": offset},
        )
