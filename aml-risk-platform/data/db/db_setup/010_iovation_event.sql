CREATE TABLE IF NOT EXISTS network.iovation_event (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    iovation_event_guid UUID NOT NULL UNIQUE,

    fk_customer_id BIGINT NOT NULL,

    fk_device_id BIGINT NOT NULL,

    integration_point VARCHAR(100),

    tracking_number BIGINT,

    event_id VARCHAR(100),

    result VARCHAR(100),

    score INTEGER,

    matched_rules TEXT,

    real_ip_address VARCHAR(50),

    stated_ip_address VARCHAR(50),

    real_ip_city VARCHAR(100),

    real_ip_region VARCHAR(100),

    real_ip_country VARCHAR(100),

    stated_ip_city VARCHAR(100),

    stated_ip_region VARCHAR(100),

    stated_ip_country VARCHAR(100),

    real_ip_proxy_type VARCHAR(100),

    stated_ip_proxy_type VARCHAR(100),

    monetary_amount NUMERIC(18,2),

    is_new_device BOOLEAN,

    observed_at TIMESTAMP NOT NULL,

    CONSTRAINT fk_iovation_customer
        FOREIGN KEY (fk_customer_id)
        REFERENCES public.customer(id),

    CONSTRAINT fk_iovation_device
        FOREIGN KEY (fk_device_id)
        REFERENCES network.device(id)
);