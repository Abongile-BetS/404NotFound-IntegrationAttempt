CREATE TABLE IF NOT EXISTS public.financial_transaction (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    transaction_guid UUID NOT NULL UNIQUE,

    fk_customer_id BIGINT NOT NULL,

    fk_transaction_type_id SMALLINT NOT NULL,

    fk_account_id BIGINT NOT NULL,

    transaction_amount NUMERIC(18,2) NOT NULL,

    tax_rate NUMERIC(10,4),

    balance NUMERIC(18,2),

    reference_comment VARCHAR(500),

    reason VARCHAR(255),

    is_cancelled BOOLEAN NOT NULL DEFAULT FALSE,

    is_paid_out BOOLEAN NOT NULL DEFAULT FALSE,

    transaction_timestamp TIMESTAMP NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_financial_transaction_customer
        FOREIGN KEY (fk_customer_id)
        REFERENCES public.customer(id),

    CONSTRAINT fk_financial_transaction_type
        FOREIGN KEY (fk_transaction_type_id)
        REFERENCES public.customer_transaction_type(id),

    CONSTRAINT fk_financial_transaction_account
        FOREIGN KEY (fk_account_id)
        REFERENCES public.account(id)

);