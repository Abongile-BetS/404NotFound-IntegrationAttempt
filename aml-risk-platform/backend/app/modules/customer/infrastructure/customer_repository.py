from app.shared.database.connection import fetch_all, fetch_one


class CustomerRepository:
    async def list_all(self):
        return await fetch_all(
            """
            SELECT
                customer_guid::text AS customer_id,
                first_name,
                last_name,
                email,
                country,
                status AS customer_status,
                NULL::text AS customer_type,
                created_at::text AS created_at
            FROM public.customer
            ORDER BY created_at DESC, id DESC
            """
        )

    async def get_by_id(self, customer_id: str):
        return await fetch_one(
            """
            SELECT
                customer_guid::text AS customer_id,
                first_name,
                last_name,
                email,
                country,
                status AS customer_status,
                NULL::text AS customer_type,
                created_at::text AS created_at
            FROM public.customer
            WHERE customer_guid::text = :customer_id
            """,
            {"customer_id": customer_id},
        )