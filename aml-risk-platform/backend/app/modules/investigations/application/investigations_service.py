from app.shared.database.connection import fetch_all, fetch_one


class InvestigationsService:
    async def list_cases(self):
        return await fetch_all(
            """
            SELECT
                ic.id,
                ic.case_guid::text AS case_id,
                ic.title,
                ic.status,
                ic.priority,
                ic.assigned_to,
                ic.outcome,
                ic.notes,
                ic.created_at::text AS created_at,
                ic.updated_at::text AS updated_at,
                c.customer_guid::text AS customer_id,
                concat_ws(' ', c.first_name, c.last_name) AS customer,
                ic.fk_alert_id AS alert_id
            FROM public.investigation_case AS ic
            LEFT JOIN public.customer AS c ON c.id = ic.fk_customer_id
            ORDER BY ic.created_at DESC, ic.id DESC
            """
        )

    async def get_case(self, case_id: int):
        return await fetch_one(
            """
            SELECT
                ic.id,
                ic.case_guid::text AS case_id,
                ic.title,
                ic.status,
                ic.priority,
                ic.assigned_to,
                ic.outcome,
                ic.notes,
                ic.created_at::text AS created_at,
                ic.updated_at::text AS updated_at,
                c.customer_guid::text AS customer_id,
                concat_ws(' ', c.first_name, c.last_name) AS customer,
                ic.fk_alert_id AS alert_id
            FROM public.investigation_case AS ic
            LEFT JOIN public.customer AS c ON c.id = ic.fk_customer_id
            WHERE ic.id = :case_id
            """,
            {"case_id": case_id},
        )

    async def create_case(
        self,
        title: str,
        customer_id: str | None = None,
        alert_id: int | None = None,
        priority: str | None = None,
        assigned_to: str | None = None,
        notes: str | None = None,
    ):
        customer = None
        if customer_id:
            customer = await fetch_one(
                "SELECT id FROM public.customer WHERE customer_guid::text = :customer_id",
                {"customer_id": customer_id},
            )
        created = await fetch_one(
            """
            INSERT INTO public.investigation_case (
                case_guid, fk_customer_id, fk_alert_id, title,
                status, priority, assigned_to, notes
            )
            VALUES (
                gen_random_uuid(), :customer_id, :alert_id, :title,
                'OPEN', :priority, :assigned_to, :notes
            )
            RETURNING id, case_guid::text AS case_id, title, status
            """,
            {
                "customer_id": customer["id"] if customer else None,
                "alert_id": alert_id,
                "title": title,
                "priority": priority,
                "assigned_to": assigned_to,
                "notes": notes,
            },
        )
        return created

    async def update_case(self, case_id: int, payload: dict):
        await fetch_one(
            """
            UPDATE public.investigation_case
            SET
                status = COALESCE(:status, status),
                priority = COALESCE(:priority, priority),
                assigned_to = COALESCE(:assigned_to, assigned_to),
                outcome = COALESCE(:outcome, outcome),
                notes = COALESCE(:notes, notes),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :case_id
            RETURNING id
            """,
            {
                "case_id": case_id,
                "status": payload.get("status"),
                "priority": payload.get("priority"),
                "assigned_to": payload.get("assigned_to"),
                "outcome": payload.get("outcome"),
                "notes": payload.get("notes"),
            },
        )
        return await self.get_case(case_id)
