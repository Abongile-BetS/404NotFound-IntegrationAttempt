from app.shared.database.connection import fetch_all


class ScreeningRepository:
    async def list_all(self):
        return await fetch_all(
            self._screening_query()
            + " ORDER BY s.screened_at DESC NULLS LAST, s.id DESC"
        )

    async def get_customer_screening(self, customer_id: str):
        return await fetch_all(
            self._screening_query()
            + " "
            "WHERE c.customer_guid::text = :customer_id "
            "ORDER BY s.screened_at DESC NULLS LAST, s.id DESC",
            {"customer_id": customer_id},
        )

    async def get_dashboard_data(self):
        results = await self.list_all()
        breakdown = await fetch_all(
            """
            SELECT COALESCE(result, 'Unknown') AS name, COUNT(*) AS value
            FROM public.screening_result
            GROUP BY result
            ORDER BY value DESC, name
            """
        )
        sources = await fetch_all(
            """
            SELECT
                COALESCE(screening_type, 'Unknown') AS name,
                COUNT(*) FILTER (WHERE match_found IS TRUE) AS matches,
                COUNT(*) AS total
            FROM public.screening_result
            GROUP BY screening_type
            ORDER BY total DESC, name
            """
        )
        trend = await fetch_all(
            """
            SELECT
                screened_at::date::text AS day,
                COUNT(*) AS screened,
                COUNT(*) FILTER (WHERE match_found IS TRUE) AS matches
            FROM public.screening_result
            WHERE screened_at IS NOT NULL
            GROUP BY screened_at::date
            ORDER BY screened_at::date DESC
            LIMIT 7
            """
        )
        trend.reverse()
        total = len(results)
        match_count = sum(1 for result in results if result["match_found"])
        cleared_count = sum(
            1
            for result in results
            if str(result["status"]).lower() in {"clear", "no match", "approved", "verified"}
        )
        return {
            "kpis": [
                {"label": "Total Screened", "value": str(total), "change": "—", "positive": True, "tone": "purple"},
                {"label": "Matched Results", "value": str(match_count), "change": "—", "positive": False, "tone": "pink"},
                {"label": "Cleared", "value": str(cleared_count), "change": "—", "positive": True, "tone": "blue"},
                {"label": "Escalated", "value": str(sum(1 for result in results if str(result["status"]).lower() in {"escalated", "confirmed match"})), "change": "—", "positive": False, "tone": "amber"},
            ],
            "trend": trend,
            "breakdown": breakdown,
            "sources": [
                {
                    "name": row["name"],
                    "matches": row["matches"],
                    "percentage": round(row["matches"] * 100 / row["total"]) if row["total"] else 0,
                }
                for row in sources
            ],
            "results": [
                {key: result[key] for key in ("id", "customer", "customerId", "source", "status", "score", "time")}
                for result in results
            ],
            "queue": [],
        }

    @staticmethod
    def _screening_query():
        return """
            SELECT
                s.screening_guid::text AS id,
                concat_ws(' ', c.first_name, c.last_name) AS customer,
                c.customer_guid::text AS "customerId",
                s.screening_type AS source,
                s.result AS status,
                NULL::text AS score,
                s.match_found,
                s.screened_at::text AS time
            FROM public.screening_result AS s
            JOIN public.customer AS c ON c.id = s.fk_customer_id
        """