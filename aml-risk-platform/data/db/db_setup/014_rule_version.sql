CREATE TABLE IF NOT EXISTS risk.rule_version (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    fk_rule_id BIGINT NOT NULL,

    version VARCHAR(50) NOT NULL,

    configuration_json JSONB NOT NULL,

    effective_from TIMESTAMP NOT NULL,

    effective_to TIMESTAMP,

    created_by VARCHAR(255),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_rule_version_rule
        FOREIGN KEY (fk_rule_id)
        REFERENCES risk.rules(id)
);