CREATE TABLE IF NOT EXISTS public.customer_transaction_type (
    id SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    transaction_type_name VARCHAR(100) NOT NULL UNIQUE,

    description VARCHAR(255)
);