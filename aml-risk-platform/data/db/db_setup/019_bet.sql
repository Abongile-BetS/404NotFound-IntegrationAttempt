CREATE TABLE IF NOT EXISTS public.bet (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    bet_guid UUID NOT NULL UNIQUE,

    fk_customer_id BIGINT NOT NULL,

    game_type VARCHAR(100) NOT NULL,
    provider VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,

    stake_amount NUMERIC(18,2) NOT NULL,
    potential_payout NUMERIC(18,2) NOT NULL,

    placed_at TIMESTAMP NOT NULL,
    settled_at TIMESTAMP,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_bet_customer
        FOREIGN KEY (fk_customer_id)
        REFERENCES public.customer(id),

    CONSTRAINT chk_bet_stake_amount
        CHECK (stake_amount >= 0),

    CONSTRAINT chk_bet_potential_payout
        CHECK (potential_payout >= 0),

    CONSTRAINT chk_bet_status
        CHECK (
            status IN (
                'PENDING',
                'OPEN',
                'WON',
                'LOST',
                'CANCELLED',
                'VOID',
                'REFUNDED'
            )
        )
);