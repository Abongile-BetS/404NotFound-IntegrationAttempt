CREATE TABLE IF NOT EXISTS risk.risk_score (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    risk_score_guid UUID NOT NULL UNIQUE,

    fk_customer_id BIGINT NOT NULL,

    score NUMERIC(10,2),

    risk_level VARCHAR(20),

    scoring_method VARCHAR(50),

    model_version VARCHAR(50),

    calculated_at TIMESTAMP,

    CONSTRAINT fk_risk_score_customer
        FOREIGN KEY (fk_customer_id)
        REFERENCES public.customer(id)
);