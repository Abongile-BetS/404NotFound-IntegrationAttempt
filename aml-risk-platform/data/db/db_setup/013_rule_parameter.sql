CREATE TABLE IF NOT EXISTS risk.rule_parameter (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    fk_rule_id BIGINT NOT NULL,

    parameter_name VARCHAR(100) NOT NULL,

    parameter_value VARCHAR(255) NOT NULL,

    data_type VARCHAR(50) NOT NULL,

    CONSTRAINT fk_rule_parameter_rule
        FOREIGN KEY (fk_rule_id)
        REFERENCES risk.rules(id)
);