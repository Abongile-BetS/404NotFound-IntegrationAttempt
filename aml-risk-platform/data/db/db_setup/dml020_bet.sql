WITH ranked_bets AS (
    SELECT
        id,
        ROW_NUMBER() OVER (ORDER BY random()) AS rn,
        COUNT(*) OVER () AS total
    FROM public.bet
),
assigned_statuses AS (
    SELECT
        id,
        CASE
            WHEN rn <= total * 0.10 THEN 'PENDING'
            WHEN rn <= total * 0.20 THEN 'OPEN'
            WHEN rn <= total * 0.40 THEN 'WON'
            WHEN rn <= total * 0.75 THEN 'LOST'
            WHEN rn <= total * 0.80 THEN 'CANCELLED'
            WHEN rn <= total * 0.85 THEN 'VOID'
            ELSE 'REFUNDED'
        END AS new_status
    FROM ranked_bets
)
UPDATE public.bet AS b
SET
    status = a.new_status,

    settled_at = CASE
        WHEN a.new_status IN ('PENDING', 'OPEN') THEN NULL
        ELSE b.placed_at
             + (1 + floor(random() * 72)) * INTERVAL '1 hour'
    END,

    potential_payout = CASE
        WHEN a.new_status = 'WON' THEN
            GREATEST(
                b.potential_payout,
                ROUND(b.stake_amount * 1.8, 2)
            )
        ELSE b.potential_payout
    END

FROM assigned_statuses AS a
WHERE b.id = a.id;

