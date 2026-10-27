from app.shared.database.connection import fetch_all, fetch_one


class KycRepository:
    async def list_all(self, limit: int = 100, offset: int = 0):
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
            LIMIT :limit OFFSET :offset
            """,
            {"limit": limit, "offset": offset},
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

    async def update_customer_kyc(
        self,
        customer_id: str,
        identity_status: str | None = None,
        address_status: str | None = None,
        verification_result: str | None = None,
    ):
        customer = await fetch_one(
            "SELECT id FROM public.customer WHERE customer_guid::text = :customer_id",
            {"customer_id": customer_id},
        )
        if customer is None:
            return None

        latest = await fetch_one(
            """
            SELECT id
            FROM public.kyc_record
            WHERE fk_customer_id = :customer_id
            ORDER BY verified_at DESC NULLS LAST, id DESC
            LIMIT 1
            """,
            {"customer_id": customer["id"]},
        )
        if latest is None:
            return await fetch_one(
                """
                INSERT INTO public.kyc_record (
                    fk_customer_id, identity_status, address_status,
                    verification_result, verified_at
                )
                VALUES (
                    :customer_id, :identity_status, :address_status,
                    :verification_result, CURRENT_TIMESTAMP
                )
                RETURNING :customer_id AS customer_id
                """,
                {
                    "customer_id": customer_id,
                    "identity_status": identity_status or "NOT_CHECKED",
                    "address_status": address_status or "NOT_CHECKED",
                    "verification_result": verification_result or "PENDING",
                },
            )

        return await fetch_one(
            """
            UPDATE public.kyc_record
            SET identity_status = COALESCE(:identity_status, identity_status),
                address_status = COALESCE(:address_status, address_status),
                verification_result = COALESCE(:verification_result, verification_result),
                verified_at = CURRENT_TIMESTAMP
            WHERE id = :kyc_id
            RETURNING :customer_id AS customer_id
            """,
            {
                "kyc_id": latest["id"],
                "customer_id": customer_id,
                "identity_status": identity_status,
                "address_status": address_status,
                "verification_result": verification_result,
            },
        )
