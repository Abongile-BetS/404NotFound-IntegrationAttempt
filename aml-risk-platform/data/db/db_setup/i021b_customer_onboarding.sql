-- ============================================================
-- PART 2
-- Create 1,000 additional onboarding applicants
--
-- These do NOT have a customer FK yet because they represent
-- onboarding applications that have not become customers.
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
    NULL,

    CASE
        WHEN n % 10 = 0 THEN 'Thabo'
        WHEN n % 10 = 1 THEN 'Liam'
        WHEN n % 10 = 2 THEN 'Sipho'
        WHEN n % 10 = 3 THEN 'Daniel'
        WHEN n % 10 = 4 THEN 'Jason'
        WHEN n % 10 = 5 THEN 'Aisha'
        WHEN n % 10 = 6 THEN 'Nomsa'
        WHEN n % 10 = 7 THEN 'Sarah'
        WHEN n % 10 = 8 THEN 'Michael'
        ELSE 'Zanele'
    END,

    CASE
        WHEN n % 10 = 0 THEN 'Mokoena'
        WHEN n % 10 = 1 THEN 'Williams'
        WHEN n % 10 = 2 THEN 'Nkosi'
        WHEN n % 10 = 3 THEN 'Smith'
        WHEN n % 10 = 4 THEN 'Naidoo'
        WHEN n % 10 = 5 THEN 'Jacobs'
        WHEN n % 10 = 6 THEN 'Dlamini'
        WHEN n % 10 = 7 THEN 'Van Wyk'
        WHEN n % 10 = 8 THEN 'Peters'
        ELSE 'Mthembu'
    END,

    -- Nationality flag
    identity_choice.is_south_african,

    -- South African: synthetic ID number
    CASE
        WHEN identity_choice.is_south_african
            THEN 'MOCKID' || LPAD(n::text, 10, '0')
        ELSE NULL
    END AS id_number,

    -- Non-South African: synthetic passport
    CASE
        WHEN NOT identity_choice.is_south_african
            THEN 'MOCKPASS' || LPAD(n::text, 8, '0')
        ELSE NULL
    END AS passport,

    ROUND(
        (8000 + random() * 92000)::numeric,
        2
    ),

    -- Unique email
    'applicant_' || n || '@mockbank.test',

    (100 + FLOOR(random() * 9900))::text || ' Main Road',

    CASE
        WHEN n % 5 = 0 THEN 'Observatory'
        WHEN n % 5 = 1 THEN 'Claremont'
        WHEN n % 5 = 2 THEN 'Bellville'
        WHEN n % 5 = 3 THEN 'Rondebosch'
        ELSE 'Century City'
    END,

    'Cape Town',
    'Western Cape',

    '+2783' || LPAD(n::text, 7, '0'),

    -- Status distribution
    CASE
        WHEN n <= 400 THEN 'PENDING'
        WHEN n <= 750 THEN 'UNDER_REVIEW'
        ELSE 'REJECTED'
    END,

    TIMESTAMP '2026-01-01'
        + (
            random() * (
                TIMESTAMP '2026-09-30'
                - TIMESTAMP '2026-01-01'
            )
        )

FROM generate_series(1, 1000) AS n

CROSS JOIN LATERAL (
    SELECT random() < 0.85 AS is_south_african
) AS identity_choice;
