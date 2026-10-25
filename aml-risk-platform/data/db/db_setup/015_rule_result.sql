CREATE TABLE IF NOT EXISTS risk.rule_result (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    rule_result_guid UUID NOT NULL UNIQUE,

    fk_customer_id BIGINT NOT NULL,

    fk_rule_id BIGINT NOT NULL,

    triggered BOOLEAN NOT NULL,

    confidence NUMERIC(5,2),

    risk_points NUMERIC(10,2),

    evaluated_at TIMESTAMP NOT NULL,

    rule_version VARCHAR(50),

    evidence_json JSONB,

    execution_time_ms INTEGER,

    CONSTRAINT fk_rule_result_customer
        FOREIGN KEY (fk_customer_id)
        REFERENCES public.customer(id),

    CONSTRAINT fk_rule_result_rule
        FOREIGN KEY (fk_rule_id)
        REFERENCES risk.rules(id)
);