CREATE TABLE IF NOT EXISTS public.screening_result (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    screening_guid UUID NOT NULL UNIQUE,

    fk_customer_id BIGINT NOT NULL,

    screening_type VARCHAR(50),

    result VARCHAR(50),

    match_found BOOLEAN,

    matched_entity VARCHAR(255),

    screened_at TIMESTAMP,

    CONSTRAINT fk_screening_customer
        FOREIGN KEY (fk_customer_id)
        REFERENCES public.customer(id)
);