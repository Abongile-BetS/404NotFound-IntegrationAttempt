CREATE TABLE IF NOT EXISTS public.investigation_case (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    case_guid UUID NOT NULL UNIQUE,

    fk_customer_id BIGINT,

    fk_alert_id BIGINT,

    title VARCHAR(255) NOT NULL,

    status VARCHAR(50) NOT NULL DEFAULT 'OPEN',

    priority VARCHAR(50),

    assigned_to VARCHAR(255),

    outcome VARCHAR(255),

    notes TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_investigation_case_customer
        FOREIGN KEY (fk_customer_id)
        REFERENCES public.customer(id),

    CONSTRAINT fk_investigation_case_alert
        FOREIGN KEY (fk_alert_id)
        REFERENCES public.alert(id)
);