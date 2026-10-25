-- ============================================================
-- MOCK DATA: bet
--
-- Generates 10 bets per existing customer.
--
-- With 11,997 customers:
--     11,997 × 10 = 119,970 bets
--
-- Status distribution:
--     10% PENDING
--     10% OPEN
--     25% WON
--     35% LOST
--      5% CANCELLED
--      5% VOID
--     10% REFUNDED
--
-- FK:
--     bet.fk_customer_id -> customer.id
-- ============================================================

INSERT INTO public.bet (
    bet_guid,
    fk_customer_id,
    game_type,
    provider,
    status,
    stake_amount,
    potential_payout,
    placed_at,
    settled_at,
    created_at
)

SELECT
    gen_random_uuid(),

    c.id,

    -- Game type
    CASE
        WHEN game_r < 0.50 THEN 'SPORTSBOOK'
        WHEN game_r < 0.75 THEN 'CASINO'
        WHEN game_r < 0.90 THEN 'LIVE_CASINO'
        ELSE 'VIRTUAL_SPORTS'
    END,

    -- Provider
    CASE
        WHEN provider_r < 0.25 THEN 'BetGames'
        WHEN provider_r < 0.50 THEN 'Evolution'
        WHEN provider_r < 0.70 THEN 'Pragmatic Play'
        WHEN provider_r < 0.85 THEN 'Hollywoodbets'
        ELSE 'Betway'
    END,

    -- Bet status
    CASE
        WHEN status_r < 0.10 THEN 'PENDING'
        WHEN status_r < 0.20 THEN 'OPEN'
        WHEN status_r < 0.45 THEN 'WON'
        WHEN status_r < 0.80 THEN 'LOST'
        WHEN status_r < 0.85 THEN 'CANCELLED'
        WHEN status_r < 0.90 THEN 'VOID'
        ELSE 'REFUNDED'
    END,

    -- Stake amount
    round(
        (
            10
            + power(stake_r, 2) * 4990
        )::numeric,
        2
    ),

    -- Potential payout
    round(
        (
            (
                10
                + power(stake_r, 2) * 4990
            )
            *
            (
                1.2
                + payout_r * 19.8
            )
        )::numeric,
        2
    ),

    -- Bet placed timestamp
    placed_at,

    -- Settled timestamp
    CASE
        WHEN status_r < 0.10
             OR status_r < 0.20
        THEN NULL

        ELSE
            placed_at
            + (
                (
                    30
                    + settlement_r * 10080
                )
                * interval '1 minute'
            )
    END,

    -- Created shortly after placement
    placed_at
        + (
            creation_r
            * interval '10 minutes'
        )

FROM public.customer AS c

-- Generate 10 bets for every customer
CROSS JOIN generate_series(1, 10) AS bet_number

-- Generate random values once per generated bet
CROSS JOIN LATERAL (
    SELECT
        random() AS game_r,
        random() AS provider_r,
        random() AS status_r,
        random() AS stake_r,
        random() AS payout_r,
        random() AS settlement_r,
        random() AS creation_r,

        timestamp '2025-01-01'
        + (
            random()
            * (
                timestamp '2026-09-30'
                - timestamp '2025-01-01'
            )
        ) AS placed_at
) AS r;-- ============================================================
-- MOCK DATA: bet
--
-- Generates 10 bets per existing customer.
--
-- With 11,997 customers:
--     11,997 × 10 = 119,970 bets
--
-- Status distribution:
--     10% PENDING
--     10% OPEN
--     25% WON
--     35% LOST
--      5% CANCELLED
--      5% VOID
--     10% REFUNDED
--
-- FK:
--     bet.fk_customer_id -> customer.id
-- ============================================================

INSERT INTO public.bet (
    bet_guid,
    fk_customer_id,
    game_type,
    provider,
    status,
    stake_amount,
    potential_payout,
    placed_at,
    settled_at,
    created_at
)

SELECT
    gen_random_uuid(),

    c.id,

    -- Game type
    CASE
        WHEN game_r < 0.50 THEN 'SPORTSBOOK'
        WHEN game_r < 0.75 THEN 'CASINO'
        WHEN game_r < 0.90 THEN 'LIVE_CASINO'
        ELSE 'VIRTUAL_SPORTS'
    END,

    -- Provider
    CASE
        WHEN provider_r < 0.25 THEN 'BetGames'
        WHEN provider_r < 0.50 THEN 'Evolution'
        WHEN provider_r < 0.70 THEN 'Pragmatic Play'
        WHEN provider_r < 0.85 THEN 'Hollywoodbets'
        ELSE 'Betway'
    END,

    -- Bet status
    CASE
        WHEN status_r < 0.10 THEN 'PENDING'
        WHEN status_r < 0.20 THEN 'OPEN'
        WHEN status_r < 0.45 THEN 'WON'
        WHEN status_r < 0.80 THEN 'LOST'
        WHEN status_r < 0.85 THEN 'CANCELLED'
        WHEN status_r < 0.90 THEN 'VOID'
        ELSE 'REFUNDED'
    END,

    -- Stake amount
    round(
        (
            10
            + power(stake_r, 2) * 4990
        )::numeric,
        2
    ),

    -- Potential payout
    round(
        (
            (
                10
                + power(stake_r, 2) * 4990
            )
            *
            (
                1.2
                + payout_r * 19.8
            )
        )::numeric,
        2
    ),

    -- Bet placed timestamp
    placed_at,

    -- Settled timestamp
    CASE
        WHEN status_r < 0.10
             OR status_r < 0.20
        THEN NULL

        ELSE
            placed_at
            + (
                (
                    30
                    + settlement_r * 10080
                )
                * interval '1 minute'
            )
    END,

    -- Created shortly after placement
    placed_at
        + (
            creation_r
            * interval '10 minutes'
        )

FROM public.customer AS c

-- Generate 10 bets for every customer
CROSS JOIN generate_series(1, 10) AS bet_number

-- Generate random values once per generated bet
CROSS JOIN LATERAL (
    SELECT
        random() AS game_r,
        random() AS provider_r,
        random() AS status_r,
        random() AS stake_r,
        random() AS payout_r,
        random() AS settlement_r,
        random() AS creation_r,

        timestamp '2025-01-01'
        + (
            random()
            * (
                timestamp '2026-09-30'
                - timestamp '2025-01-01'
            )
        ) AS placed_at
) AS r;