CREATE TABLE IF NOT EXISTS risk.risk_event (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    risk_event_guid UUID NOT NULL UNIQUE,

    fk_customer_id BIGINT NOT NULL,

    fk_rule_result_id BIGINT,

    event_type VARCHAR(100) NOT NULL,

    severity VARCHAR(50) NOT NULL,

    status VARCHAR(50) NOT NULL,

    detected_at TIMESTAMP NOT NULL,

    CONSTRAINT fk_risk_event_customer
        FOREIGN KEY (fk_customer_id)
        REFERENCES public.customer(id),

    CONSTRAINT fk_risk_event_result
        FOREIGN KEY (fk_rule_result_id)
        REFERENCES risk.rule_result(id)
);
