CREATE TABLE IF NOT EXISTS public.customer_onboarding (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    onboarding_guid UUID NOT NULL UNIQUE,

    fk_customer_id BIGINT,

    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,

    is_south_african BOOLEAN,
    id_number VARCHAR(30) UNIQUE,
    passport VARCHAR(30) UNIQUE,

    salary NUMERIC(18,2),

    email VARCHAR(255) NOT NULL UNIQUE,

    street_address VARCHAR(255),
    suburb VARCHAR(100),
    city VARCHAR(100),
    province VARCHAR(100),

    phone_number VARCHAR(30),

    onboarding_status VARCHAR(50) NOT NULL DEFAULT 'PENDING',

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_customer_onboarding_customer
        FOREIGN KEY (fk_customer_id)
        REFERENCES public.customer(id),

    CONSTRAINT chk_customer_onboarding_salary
        CHECK (salary >= 0),

    CONSTRAINT chk_customer_onboarding_status
        CHECK (
            onboarding_status IN (
                'PENDING',
                'APPROVED',
                'REJECTED',
                'UNDER_REVIEW'
            )
        ),


    CONSTRAINT chk_id_or_passport
    CHECK (
        id_number IS NOT NULL
        OR passport IS NOT NULL
    ),

    CONSTRAINT chk_onboarding_identity_document
    CHECK (
        (
            is_south_african = TRUE
            AND id_number IS NOT NULL
            AND passport IS NULL
        )
        OR
        (
            is_south_african = FALSE
            AND passport IS NOT NULL
            AND id_number IS NULL
        )
    )
);