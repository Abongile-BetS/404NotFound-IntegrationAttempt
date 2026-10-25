WITH expected_transactions AS (
    -- Every bet should have a stake transaction.
    SELECT
        b.id AS fk_bet_id,
        b.fk_customer_id,
        b.stake_amount AS transaction_amount,
        'STAKE'::varchar(50) AS transaction_type,
        b.placed_at AS event_time,
        'Stake placed'::varchar(500) AS reference_comment
    FROM public.bet AS b

    UNION ALL

    -- Winning bets receive a payout.
    SELECT
        b.id,
        b.fk_customer_id,
        b.potential_payout,
        'PAYOUT'::varchar(50),
        COALESCE(b.settled_at, b.placed_at),
        'Payout for winning bet'
    FROM public.bet AS b
    WHERE b.status = 'WON'
      AND b.potential_payout > 0

    UNION ALL

    -- Cancelled and void bets return the stake.
    SELECT
        b.id,
        b.fk_customer_id,
        b.stake_amount,
        'STAKE_RETURN'::varchar(50),
        COALESCE(b.settled_at, b.placed_at),
        CASE
            WHEN b.status = 'CANCELLED'
                THEN 'Stake returned: cancelled bet'
            ELSE 'Stake returned: void bet'
        END
    FROM public.bet AS b
    WHERE b.status IN ('CANCELLED', 'VOID')
      AND b.stake_amount > 0

    UNION ALL

    -- Refunded bets receive a refund.
    SELECT
        b.id,
        b.fk_customer_id,
        b.stake_amount,
        'REFUND'::varchar(50),
        COALESCE(b.settled_at, b.placed_at),
        'Stake refunded'
    FROM public.bet AS b
    WHERE b.status = 'REFUNDED'
      AND b.stake_amount > 0
),
transactions_with_accounts AS (
    SELECT
        e.*,
        a.id AS fk_account_id
    FROM expected_transactions AS e
    JOIN LATERAL (
        SELECT acc.id
        FROM public.account AS acc
        WHERE acc.fk_customer_id = e.fk_customer_id
        ORDER BY acc.id
        LIMIT 1
    ) AS a ON TRUE
)
INSERT INTO public.bet_transaction (
    bet_transaction_guid,
    fk_bet_id,
    fk_customer_id,
    fk_account_id,
    transaction_type,
    transaction_amount,
    reference_comment,
    created_at
)
SELECT
    gen_random_uuid(),
    e.fk_bet_id,
    e.fk_customer_id,
    e.fk_account_id,
    e.transaction_type,
    e.transaction_amount,
    e.reference_comment,
    e.event_time
FROM transactions_with_accounts AS e
WHERE NOT EXISTS (
    SELECT 1
    FROM public.bet_transaction AS existing
    WHERE existing.fk_bet_id = e.fk_bet_id
      AND existing.transaction_type = e.transaction_type
);
