from app.shared.database.connection import fetch_all, fetch_one


class ScreeningRepository:
    async def list_all(
        self,
        limit: int = 100,
        offset: int = 0,
    ):
        return await fetch_all(
            self._screening_query()
            + " ORDER BY s.screened_at DESC NULLS LAST, s.id DESC "
            "LIMIT :limit OFFSET :offset",
            {"limit": limit, "offset": offset},
        )

    async def get_customer_screening(
        self,
        customer_id: str,
        limit: int = 100,
        offset: int = 0,
    ):
        return await fetch_all(
            self._screening_query() + " WHERE c.customer_guid::text = :customer_id "
            "ORDER BY s.screened_at DESC NULLS LAST, s.id DESC "
            "LIMIT :limit OFFSET :offset",
            {
                "customer_id": customer_id,
                "limit": limit,
                "offset": offset,
            },
        )

    async def get_dashboard_data(self, limit: int = 100, offset: int = 0):
        results = await self.list_all(limit=limit, offset=offset)
        counts = await fetch_all(
            """
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE match_found IS TRUE) AS matched,
                COUNT(*) FILTER (
                    WHERE lower(COALESCE(result, '')) IN
                        ('clear', 'no match', 'approved', 'verified')
                ) AS cleared,
                COUNT(*) FILTER (
                    WHERE lower(COALESCE(result, '')) IN
                        ('escalated', 'confirmed match')
                ) AS escalated
            FROM public.screening_result
            """
        )
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
        summary = counts[0]
        return {
            "kpis": [
                {
                    "label": "Total Screened",
                    "value": str(summary["total"]),
                    "change": "—",
                    "positive": True,
                    "tone": "purple",
                },
                {
                    "label": "Matched Results",
                    "value": str(summary["matched"]),
                    "change": "—",
                    "positive": False,
                    "tone": "pink",
                },
                {
                    "label": "Cleared",
                    "value": str(summary["cleared"]),
                    "change": "—",
                    "positive": True,
                    "tone": "blue",
                },
                {
                    "label": "Escalated",
                    "value": str(summary["escalated"]),
                    "change": "—",
                    "positive": False,
                    "tone": "amber",
                },
            ],
            "trend": trend,
            "breakdown": breakdown,
            "sources": [
                {
                    "name": row["name"],
                    "matches": row["matches"],
                    "percentage": round(row["matches"] * 100 / row["total"])
                    if row["total"]
                    else 0,
                }
                for row in sources
            ],
            "results": [
                {
                    key: result[key]
                    for key in (
                        "id",
                        "customer",
                        "customerId",
                        "source",
                        "status",
                        "score",
                        "time",
                    )
                }
                for result in results
            ],
            "queue": [],
        }

    async def update_result(
        self,
        screening_id: str,
        result: str | None = None,
        match_found: bool | None = None,
    ):
        return await fetch_one(
            """
            UPDATE public.screening_result
            SET result = COALESCE(:result, result),
                match_found = COALESCE(:match_found, match_found)
            WHERE screening_guid::text = :screening_id
            RETURNING screening_guid::text AS id, result, match_found
            """,
            {
                "screening_id": screening_id,
                "result": result,
                "match_found": match_found,
            },
        )

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
