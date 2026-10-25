CREATE TABLE IF NOT EXISTS raw.iovation (

    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Event
    event_timestamp TIMESTAMPTZ,
    tracking_number BIGINT,
    result VARCHAR(50),
    integration_point VARCHAR(100),
    rule_set VARCHAR(255),
    rule_count INTEGER,
    matched_rules TEXT,
    remote_tool_detected VARCHAR(10),
    rule_name TEXT,
    score INTEGER,

    -- Risk Scores
    stated_ip_botnet_score INTEGER,
    iovation_ip_botnet_score INTEGER,
    real_ip_botnet_score INTEGER,
    behavioral_analytics_score INTEGER,
    surescore_global NUMERIC(10,4),
    surescore_vertical NUMERIC(10,4),

    -- Tenant / Account
    tenant_id VARCHAR(100),
    account_code VARCHAR(100),
    device_id VARCHAR(255),

    -- Real IP
    real_ip_address VARCHAR(50),
    real_ip_proxy_type VARCHAR(100),
    real_ip_anonymous_proxy VARCHAR(10),
    real_ip_isp VARCHAR(255),
    real_ip_isp_org VARCHAR(255),
    real_ip_city VARCHAR(100),
    real_ip_region VARCHAR(100),
    real_ip_country VARCHAR(100),

    -- Stated IP
    stated_ip_address VARCHAR(50),
    stated_ip_proxy_type VARCHAR(100),
    stated_ip_anonymous_proxy VARCHAR(10),
    stated_isp VARCHAR(255),
    stated_isp_org VARCHAR(255),
    stated_city VARCHAR(100),
    stated_region VARCHAR(100),
    stated_country VARCHAR(100),

    -- iovation IP
    iovation_ip_address VARCHAR(50),
    iovation_ip_proxy_type VARCHAR(100),
    iovation_ip_anonymous_proxy VARCHAR(10),
    iovation_isp VARCHAR(255),
    iovation_isp_org VARCHAR(255),
    iovation_city VARCHAR(100),
    iovation_region VARCHAR(100),
    iovation_country VARCHAR(100),

    -- Device
    blackbox_age VARCHAR(100),
    blackbox_date TIMESTAMPTZ,
    new_device VARCHAR(10),
    device_type VARCHAR(100),
    recognition_source VARCHAR(100),
    operating_system VARCHAR(100),
    screen_resolution VARCHAR(50),
    screen_resolution_irreducible VARCHAR(50),
    browser_language VARCHAR(50),
    browser_type VARCHAR(100),
    browser_version VARCHAR(100),
    browser_timezone VARCHAR(50),
    flash_enabled VARCHAR(10),
    flash_storage_enabled VARCHAR(10),
    flash_version VARCHAR(50),

    -- IDs
    event_id VARCHAR(100),
    service_id VARCHAR(100),
    online_id VARCHAR(100),

    -- Email
    email_address VARCHAR(255),
    email_verified VARCHAR(10),

    -- Billing
    billing_street TEXT,
    billing_city VARCHAR(100),
    billing_region VARCHAR(100),
    billing_country VARCHAR(100),
    billing_postal_code VARCHAR(20),

    -- Shipping
    shipping_street TEXT,
    shipping_city VARCHAR(100),
    shipping_region VARCHAR(100),
    shipping_country VARCHAR(100),
    shipping_postal_code VARCHAR(20),
    billing_shipping_mismatch VARCHAR(10),

    -- Transaction
    monetary_amount NUMERIC(18,2),
    currency_type VARCHAR(10),
    credit_card_bin VARCHAR(50),
    ach_routing_number VARCHAR(50),

    -- Contact
    home_phone_number VARCHAR(50),
    mobile_phone_number VARCHAR(50),
    office_phone_number VARCHAR(50),

    -- Misc
    referrer_url TEXT,
    alternate_ip VARCHAR(50),
    sku VARCHAR(255),
    upc VARCHAR(255),
    session_alias VARCHAR(255),
    national_id_issuer VARCHAR(255),
    security_pin VARCHAR(255),
    security_pin_type VARCHAR(100),
    home_phone_verified VARCHAR(10),
    home_phone_sms_enabled VARCHAR(10),
    mobile_phone_verified VARCHAR(10),
    mobile_phone_sms_enabled VARCHAR(10),
    office_phone_verified VARCHAR(10),
    office_phone_sms_enabled VARCHAR(10),

    -- Geolocation
    gps_spoofing_detected VARCHAR(10),
    gps_spoofing_type VARCHAR(100),
    latitude_longitude VARCHAR(100),
    altitude NUMERIC(18,4),
    geolocation_timestamp TIMESTAMPTZ,
    geolocation_accuracy NUMERIC(18,4),

    -- SIM / Network
    sim_service VARCHAR(100),
    sim_service_country VARCHAR(100),
    carrier_name VARCHAR(255),
    carrier_country VARCHAR(100),

    -- Device Hardware
    device_hardware_id VARCHAR(255),
    device_manufacturer VARCHAR(255),
    device_brand_name VARCHAR(255),
    model_id VARCHAR(100),
    device_language VARCHAR(50),
    device_currency VARCHAR(20),
    device_orientation VARCHAR(50),
    system_uptime BIGINT,
    charging_status VARCHAR(50),
    cellular_network_type VARCHAR(100),
    hostname VARCHAR(255),
    android_sdk_level INTEGER,
    allow_non_market_apps VARCHAR(10),

    -- Device Security
    jailbreak_root_detected VARCHAR(10),
    root_evasion_indicated VARCHAR(10),
    debug_mode_enabled VARCHAR(10),
    executable_name VARCHAR(255),
    application_name VARCHAR(255),
    application_version VARCHAR(100),
    application_orientation VARCHAR(50),
    application_signer_id VARCHAR(255),
    application_bundle_id VARCHAR(255),
    application_process_name VARCHAR(255),

    -- Display / Environment
    screen_color_depth INTEGER,
    virtual_environment_detected VARCHAR(10),
    private_browsing_indicator VARCHAR(10),

    -- Transaction / Model Rules
    transaction_field_rules TEXT,

    -- SureScore / Models
    surescore_primary NUMERIC(10,4),
    surescore_preview NUMERIC(10,4),
    advanced_transaction_model_primary NUMERIC(10,4),
    advanced_transaction_model_preview NUMERIC(10,4),
    behavioral_model_primary NUMERIC(10,4),
    behavioral_model_preview NUMERIC(10,4),
    behavioral_analytics_score_raw NUMERIC(18,4),

    -- Fraud / IP Signals
    fraud_ring_indicator VARCHAR(50),
    ip_signal_score_iovation_ip NUMERIC(10,4),
    ip_signal_score_stated_ip NUMERIC(10,4),
    ip_signal_score_real_ip NUMERIC(10,4),

    last_ip_signal_score_iovation_ip NUMERIC(10,4),
    last_ip_signal_score_stated_ip NUMERIC(10,4),
    last_ip_signal_score_real_ip NUMERIC(10,4),

    ip_signal_result_codes_iovation_ip TEXT,
    ip_signal_result_codes_stated_ip TEXT,
    ip_signal_result_codes_real_ip TEXT,

    ip_signal_score_change_date_iovation_ip TIMESTAMPTZ,
    ip_signal_score_change_date_stated_ip TIMESTAMPTZ,
    ip_signal_score_change_date_real_ip TIMESTAMPTZ,

    -- Transaction Billing
    transaction_field_tu_billing_id VARCHAR(255), 
    CONSTRAINT uq_iovation_tracking_number UNIQUE (tracking_number)
);