CREATE TABLE IF NOT EXISTS network.device (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    device_guid UUID NOT NULL UNIQUE,

    source_device_id VARCHAR(255) NOT NULL UNIQUE,

    device_type VARCHAR(100),

    operating_system VARCHAR(100),

    browser_type VARCHAR(100),

    browser_version VARCHAR(50),

    browser_language VARCHAR(50),

    screen_resolution VARCHAR(50),

    device_manufacturer VARCHAR(100),

    device_brand_name VARCHAR(100),

    model_id VARCHAR(100),

    device_language VARCHAR(50)
);