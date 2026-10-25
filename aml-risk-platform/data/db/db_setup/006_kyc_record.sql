CREATE TABLE IF NOT EXISTS public.kyc_record (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    kyc_guid UUID NOT NULL UNIQUE,

    fk_customer_id BIGINT NOT NULL,

    identity_status VARCHAR(50),

    address_status VARCHAR(50),

    verification_result VARCHAR(50),

    verified_at TIMESTAMP,

    CONSTRAINT fk_kyc_customer
        FOREIGN KEY (fk_customer_id)
        REFERENCES public.customer(id)
);