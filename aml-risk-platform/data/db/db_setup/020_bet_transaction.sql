CREATE TABLE IF NOT EXISTS public.bet_transaction (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    bet_transaction_guid UUID NOT NULL UNIQUE,

    fk_bet_id BIGINT NOT NULL,
    fk_customer_id BIGINT NOT NULL,
    fk_account_id BIGINT NOT NULL,

    transaction_type VARCHAR(50) NOT NULL,

    transaction_amount NUMERIC(18,2) NOT NULL,

    tax_rate NUMERIC(10,4),
    balance NUMERIC(18,2),
    currency_rate NUMERIC(18,6),

    reference_comment VARCHAR(500),

    branch_id VARCHAR(100),
    reason_id VARCHAR(100),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_bet_transaction_bet
        FOREIGN KEY (fk_bet_id)
        REFERENCES public.bet(id),

    CONSTRAINT fk_bet_transaction_customer
        FOREIGN KEY (fk_customer_id)
        REFERENCES public.customer(id),

    CONSTRAINT fk_bet_transaction_account
        FOREIGN KEY (fk_account_id)
        REFERENCES public.account(id),

    CONSTRAINT chk_bet_transaction_amount
        CHECK (transaction_amount >= 0),

    CONSTRAINT chk_bet_transaction_type
        CHECK (
            transaction_type IN (
                'STAKE',
                'STAKE_RETURN',
                'PAYOUT',
                'REFUND'
            )
        )
);