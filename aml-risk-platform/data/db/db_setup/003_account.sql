CREATE TABLE IF NOT EXISTS public.account (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    account_guid UUID NOT NULL UNIQUE,

    src_account_code varchar(100) NOT NULL,

    fk_customer_id BIGINT NOT NULL,

    status VARCHAR(50) NOT NULL,

    balance NUMERIC(18,2) NOT NULL DEFAULT 0.00,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT account_src_account_code_key UNIQUE (src_account_code),

    CONSTRAINT fk_account_customer
        FOREIGN KEY (fk_customer_id)
        REFERENCES public.customer(id)
);