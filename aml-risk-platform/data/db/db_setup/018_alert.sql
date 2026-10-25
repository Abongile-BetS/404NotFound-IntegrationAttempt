CREATE TABLE IF NOT EXISTS public.alert (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    alert_guid UUID NOT NULL UNIQUE,

    fk_customer_id BIGINT NOT NULL,

    fk_risk_score_id BIGINT NOT NULL,

    alert_type VARCHAR(100),

    severity VARCHAR(50),

    status VARCHAR(50),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_alert_customer
        FOREIGN KEY (fk_customer_id)
        REFERENCES public.customer(id),

    CONSTRAINT fk_alert_risk_score
        FOREIGN KEY (fk_risk_score_id)
        REFERENCES risk.risk_score(id)
);