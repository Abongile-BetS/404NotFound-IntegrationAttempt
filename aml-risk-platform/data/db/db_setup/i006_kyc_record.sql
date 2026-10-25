-- ============================================================
-- MOCK DATA: kyc_record
-- Creates one KYC record for every existing customer
-- ============================================================

INSERT INTO public.kyc_record (
    kyc_guid,
    fk_customer_id,
    identity_status,
    address_status,
    verification_result,
    verified_at
)

SELECT
    gen_random_uuid(),

    c.id,

    -- Identity verification status
    CASE
        WHEN r < 0.85 THEN 'Verified'
        WHEN r < 0.95 THEN 'Pending'
        ELSE 'Failed'
    END,

    -- Address verification status
    CASE
        WHEN r2 < 0.80 THEN 'Verified'
        WHEN r2 < 0.95 THEN 'Pending'
        ELSE 'Failed'
    END,

    -- Overall KYC result
    CASE
        WHEN r < 0.75 THEN 'Approved'
        WHEN r < 0.90 THEN 'Pending'
        WHEN r < 0.97 THEN 'Rejected'
        ELSE 'Manual Review'
    END,

    -- Only completed KYC records receive a verification date
    CASE
        WHEN r < 0.90 THEN
            timestamp '2025-01-01'
            + (
                random()
                * (
                    timestamp '2026-09-30'
                    - timestamp '2025-01-01'
                )
            )
        ELSE NULL
    END

FROM public.customer AS c

CROSS JOIN LATERAL (
    SELECT
        random() AS r,
        random() AS r2
) AS random_values

-- Prevent duplicate KYC records for the same customer
WHERE NOT EXISTS (
    SELECT 1
    FROM public.kyc_record AS existing
    WHERE existing.fk_customer_id = c.id
);