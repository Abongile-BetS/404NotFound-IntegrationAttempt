INSERT INTO public.financial_transaction (
    transaction_guid,
    fk_customer_id,
    fk_transaction_type_id,
    fk_account_id,
    transaction_amount,
    tax_rate,
    balance,
    reference_comment,
    reason,
    is_cancelled,
    is_paid_out,
    transaction_timestamp
)
SELECT
    gen_random_uuid(),

    a.fk_customer_id,

    CASE
        WHEN r < 0.60 THEN 9
        WHEN r < 0.72 THEN 8
        WHEN r < 0.82 THEN 11
        WHEN r < 0.92 THEN 12
        ELSE 14
    END,

    a.id,

    -- Withdrawal amount: R100 - R10,000
    ROUND((100 + random() * 9900)::numeric, 2),

    0,

    NULL,

    'Account Withdrawal',

    'Customer Withdrawal',

    false,

    false,

    TIMESTAMP '2025-01-01'
        + (
            random() *
            (
                TIMESTAMP '2026-09-30'
                - TIMESTAMP '2025-01-01'
            )
        )

FROM generate_series(1, 2000)

CROSS JOIN LATERAL (
    SELECT
        random() AS r
) distribution

CROSS JOIN LATERAL (
    SELECT
        id,
        fk_customer_id
    FROM public.account
    ORDER BY random()
    LIMIT 1
) a;