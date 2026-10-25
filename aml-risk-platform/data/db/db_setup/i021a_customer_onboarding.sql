-- ============================================================
-- MOCK DATA: customer_onboarding
--
-- 1. Creates one APPROVED onboarding record for every
--    existing customer.
--
-- 2. Creates 1,000 additional onboarding records representing
--    applicants who have not yet been linked to a customer.
--
--    Extra records:
--      PENDING       = 40%
--      UNDER_REVIEW  = 35%
--      REJECTED      = 25%
--
-- 3. Uses generated IDs/emails to satisfy UNIQUE constraints.
-- ============================================================



-- ============================================================
-- MOCK DATA: customer_onboarding
-- PART 1: One APPROVED onboarding record per existing customer
-- ============================================================

INSERT INTO public.customer_onboarding (
    onboarding_guid,
    fk_customer_id,
    first_name,
    last_name,
    is_south_african,
    id_number,
    passport,
    salary,
    email,
    street_address,
    suburb,
    city,
    province,
    phone_number,
    onboarding_status,
    created_at
)

SELECT
    gen_random_uuid(),

    c.id,

    c.first_name,
    c.last_name,

    
    -- Choose the customer type once per record
    identity_choice.is_south_african,

    -- South African: generate an ID number
    CASE
        WHEN identity_choice.is_south_african
            THEN 'MOCKID' || LPAD(c.id::text, 10, '0')
        ELSE NULL
    END AS id_number,

    -- Non-South African: generate a passport number
    CASE
        WHEN NOT identity_choice.is_south_african
            THEN 'MOCKPASS' || LPAD(c.id::text, 8, '0')
        ELSE NULL
    END AS passport,

    -- Synthetic salary
    ROUND(
        (8000 + random() * 92000)::numeric,
        2
    ),

    -- Guaranteed unique email
    'customer_' || c.id || '@mockbank.test',

    -- Synthetic address
    (100 + FLOOR(random() * 9900))::text || ' Main Road',

    CASE
        WHEN random() < 0.20 THEN 'Observatory'
        WHEN random() < 0.40 THEN 'Claremont'
        WHEN random() < 0.60 THEN 'Bellville'
        WHEN random() < 0.80 THEN 'Rondebosch'
        ELSE 'Century City'
    END,

    'Cape Town',
    'Western Cape',

    -- Synthetic phone number
    '+2782' || LPAD((c.id % 10000000)::text, 7, '0'),

    'APPROVED',

    TIMESTAMP '2025-01-01'
        + (
            random() * (
                TIMESTAMP '2026-09-30'
                - TIMESTAMP '2025-01-01'
            )
        )

FROM public.customer AS c

CROSS JOIN LATERAL (
    SELECT random() < 0.85 AS is_south_african
) AS identity_choice

WHERE NOT EXISTS (
    SELECT 1
    FROM public.customer_onboarding AS co
    WHERE co.fk_customer_id = c.id
);