from app.modules.workspace.api.workspace_router import get_workspace_data
from app.shared.database.connection import fetch_all, fetch_one


class ReportingService:
    async def get_home_workspace(self):
        return await get_workspace_data("dashboard")

    async def get_executive_workspace(self):
        return await get_workspace_data("executive")

    async def get_dashboard(self):
        counts = await fetch_one(
            """
            SELECT
                (SELECT COUNT(*) FROM public.customer) AS customers,
                (SELECT COUNT(*) FROM public.kyc_record
                 WHERE lower(COALESCE(verification_result, '')) IN ('pending', 'manual review')) AS kyc_pending,
                (SELECT COUNT(*) FROM public.kyc_record
                 WHERE lower(COALESCE(verification_result, '')) IN ('approved', 'verified')) AS kyc_verified,
                (SELECT COUNT(*) FROM public.kyc_record
                 WHERE lower(COALESCE(verification_result, '')) IN ('rejected', 'failed')) AS kyc_action_required
            """
        )
        if counts is None:
            raise RuntimeError("Unable to retrieve reporting totals")
        activity = await fetch_all(
            """
            SELECT
                c.customer_guid::text AS id,
                concat_ws(' ', c.first_name, c.last_name) AS name,
                COALESCE(k.verification_result, c.status) AS status,
                c.created_at::text AS date,
                k.verified_at::text AS verified_at
            FROM public.customer AS c
            LEFT JOIN LATERAL (
                SELECT verification_result, verified_at
                FROM public.kyc_record
                WHERE fk_customer_id = c.id
                ORDER BY verified_at DESC NULLS LAST, id DESC
                LIMIT 1
            ) AS k ON TRUE
            ORDER BY c.created_at DESC, c.id DESC
            LIMIT 10
            """
        )
        queue = await fetch_all(
            """
            SELECT
                co.onboarding_guid::text AS customer,
                concat_ws(' ', co.first_name, co.last_name) AS name,
                co.onboarding_status AS verification,
                co.created_at::text AS waiting
            FROM public.customer_onboarding AS co
            WHERE upper(co.onboarding_status) IN ('PENDING', 'UNDER_REVIEW')
            ORDER BY co.created_at, co.id
            LIMIT 10
            """
        )
        trend = await fetch_all(
            """
            SELECT
                created_at::date::text AS day,
                COUNT(*) FILTER (WHERE upper(onboarding_status) = 'APPROVED') AS verified,
                COUNT(*) FILTER (WHERE upper(onboarding_status) IN ('PENDING', 'UNDER_REVIEW')) AS pending,
                COUNT(*) FILTER (WHERE upper(onboarding_status) = 'REJECTED') AS action,
                COUNT(*) AS started
            FROM public.customer_onboarding
            GROUP BY created_at::date
            ORDER BY created_at::date DESC
            LIMIT 7
            """
        )
        trend.reverse()
        documents = await fetch_all(
            """
            SELECT document_type AS name, COUNT(*) AS count
            FROM public.customer_identity_document
            GROUP BY document_type
            ORDER BY document_type
            """
        )
        return {
            "kpis": [
                {"label": "Total Customers", "value": str(counts["customers"]), "change": "—", "positive": True, "tone": "purple", "points": []},
                {"label": "KYC Pending", "value": str(counts["kyc_pending"]), "change": "—", "positive": False, "tone": "pink", "points": []},
                {"label": "Verified Customers", "value": str(counts["kyc_verified"]), "change": "—", "positive": True, "tone": "blue", "points": []},
                {"label": "Requires Action", "value": str(counts["kyc_action_required"]), "change": "—", "positive": False, "tone": "amber", "points": []},
            ],
            "activity": [
                {
                    "id": row["id"],
                    "name": row["name"],
                    "status": row["status"] or "Unknown",
                    "date": row["date"],
                    "time": row["verified_at"] or "Not verified",
                }
                for row in activity
            ],
            "verification_queue": [
                {
                    "customer": row["customer"],
                    "name": row["name"],
                    "verification": row["verification"],
                    "priority": row["verification"],
                    "waiting": row["waiting"],
                    "tone": "amber",
                }
                for row in queue
            ],
            "trend": [
                {
                    "day": row["day"],
                    "verified": row["verified"],
                    "pending": row["pending"],
                    "action": row["action"],
                    "started": row["started"],
                }
                for row in trend
            ],
            "document_types": [
                {"name": row["name"], "value": str(row["count"])}
                for row in documents
            ],
        }

    async def get_summary(self):
        summary = await fetch_one(
            """
            SELECT
                (SELECT COUNT(*) FROM public.customer) AS customer_count,
                (SELECT COUNT(*) FROM public.alert
                 WHERE upper(COALESCE(status, '')) IN ('OPEN', 'IN_REVIEW', 'PENDING')) AS open_alert_count,
                0::bigint AS open_case_count,
                (SELECT COUNT(*) FROM public.financial_transaction) AS transaction_count
            """
        )
        if summary is None:
            raise RuntimeError("Unable to retrieve reporting summary")
        return summary
