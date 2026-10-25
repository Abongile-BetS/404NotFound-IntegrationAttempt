from app.shared.database.connection import fetch_all, fetch_one


class KycRepository:
    async def list_all(self):
        return await fetch_all(
            """
            SELECT
                c.customer_guid::text AS customer_id,
                k.identity_status,
                k.address_status,
                k.verification_result
            FROM public.kyc_record AS k
            JOIN public.customer AS c ON c.id = k.fk_customer_id
            ORDER BY k.verified_at DESC NULLS LAST, k.id DESC
            """
        )

    async def get_customer_kyc(self, customer_id: str):
        return await fetch_one(
            """
            SELECT
                c.customer_guid::text AS customer_id,
                k.identity_status,
                k.address_status,
                k.verification_result
            FROM public.kyc_record AS k
            JOIN public.customer AS c ON c.id = k.fk_customer_id
            WHERE c.customer_guid::text = :customer_id
            ORDER BY k.verified_at DESC NULLS LAST, k.id DESC
            LIMIT 1
            """,
            {"customer_id": customer_id},
        )