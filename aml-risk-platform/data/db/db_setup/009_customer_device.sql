CREATE TABLE IF NOT EXISTS network.customer_device (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    fk_customer_id BIGINT NOT NULL,

    fk_device_id BIGINT NOT NULL,

    first_seen TIMESTAMP,

    last_seen TIMESTAMP,

    is_new_device BOOLEAN,

    CONSTRAINT fk_customer_device_customer
        FOREIGN KEY (fk_customer_id)
        REFERENCES public.customer(id),

    CONSTRAINT fk_customer_device_device
        FOREIGN KEY (fk_device_id)
        REFERENCES network.device(id),

    CONSTRAINT uq_customer_device
        UNIQUE (fk_customer_id, fk_device_id)
);
