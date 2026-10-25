CREATE TABLE IF NOT EXISTS public.customer (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    customer_guid UUID NOT NULL UNIQUE,

    customer_title VARCHAR(20),

    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,

    date_of_birth DATE NOT NULL,

    email VARCHAR(255),

    cellphone VARCHAR(20),

    gender VARCHAR(20),

    country VARCHAR(100),
    country_of_origin VARCHAR(100),

    status VARCHAR(50) NOT NULL,

    customer_fica_compliant BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT customer_email_unique UNIQUE (email)

);