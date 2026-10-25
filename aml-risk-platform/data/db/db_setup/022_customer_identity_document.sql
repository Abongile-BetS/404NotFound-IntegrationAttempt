CREATE TABLE IF NOT EXISTS public.customer_identity_document (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    document_guid UUID NOT NULL UNIQUE,

    fk_customer_id BIGINT NOT NULL,

    document_type VARCHAR(30) NOT NULL,
    document_number_encrypted BYTEA NOT NULL,

    issuing_country VARCHAR(100) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_identity_document_customer
        FOREIGN KEY (fk_customer_id)
        REFERENCES public.customer(id),

    CONSTRAINT chk_identity_document_type
        CHECK (
            document_type IN (
                'NATIONAL_ID',
                'PASSPORT'
            )
        )
);