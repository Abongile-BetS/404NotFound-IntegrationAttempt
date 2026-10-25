
BEGIN;

-- 1. Create sample AML rules.
INSERT INTO risk.rules (
    rule_guid, code, name, category, description,
    rule_type, severity, risk_weight, enabled, version
)
VALUES
(
    '11111111-1111-4111-8111-111111111101',
    'HIGH_VALUE_DEPOSIT',
    'High Value Deposit',
    'TRANSACTION',
    'Demo rule for deposits exceeding an illustrative threshold.',
    'THRESHOLD',
    'HIGH',
    30,
    TRUE,
    '1.0'
),
(
    '11111111-1111-4111-8111-111111111102',
    'REPEATED_DEPOSIT',
    'Repeated Deposit Activity',
    'TRANSACTION',
    'Demo rule for repeated deposit activity.',
    'VELOCITY',
    'MEDIUM',
    25,
    TRUE,
    '1.0'
),
(
    '11111111-1111-4111-8111-111111111103',
    'HIGH_VALUE_BETTING',
    'High Value Betting Activity',
    'BETTING',
    'Demo rule for high value betting activity.',
    'THRESHOLD',
    'HIGH',
    20,
    TRUE,
    '1.0'
)
ON CONFLICT (code) DO NOTHING;


-- 2. Add parameters for each rule.
INSERT INTO risk.rule_parameter (
    fk_rule_id, parameter_name, parameter_value, data_type
)
SELECT r.id, p.parameter_name, p.parameter_value, p.data_type
FROM (
    VALUES
        ('HIGH_VALUE_DEPOSIT', 'threshold_amount', '10000', 'numeric'),
        ('REPEATED_DEPOSIT', 'minimum_count', '3', 'integer'),
        ('HIGH_VALUE_BETTING', 'threshold_amount', '5000', 'numeric')
) AS p(code, parameter_name, parameter_value, data_type)
JOIN risk.rules r ON r.code = p.code
WHERE NOT EXISTS (
    SELECT 1
    FROM risk.rule_parameter existing
    WHERE existing.fk_rule_id = r.id
      AND existing.parameter_name = p.parameter_name
);


-- 3. Create version 1.0 of each rule.
INSERT INTO risk.rule_version (
    fk_rule_id, version, configuration_json,
    effective_from, created_by
)
SELECT
    r.id,
    '1.0',
    CASE r.code
        WHEN 'HIGH_VALUE_DEPOSIT' THEN
            '{"threshold_amount": 10000}'::jsonb
        WHEN 'REPEATED_DEPOSIT' THEN
            '{"minimum_count": 3}'::jsonb
        WHEN 'HIGH_VALUE_BETTING' THEN
            '{"threshold_amount": 5000}'::jsonb
    END,
    TIMESTAMP '2026-10-16 00:00:00',
    'demo_seed'
FROM risk.rules r
WHERE r.code IN (
    'HIGH_VALUE_DEPOSIT',
    'REPEATED_DEPOSIT',
    'HIGH_VALUE_BETTING'
)
AND NOT EXISTS (
    SELECT 1
    FROM risk.rule_version v
    WHERE v.fk_rule_id = r.id
      AND v.version = '1.0'
);


-- 4. Generate illustrative rule evaluation results
-- for up to 20 existing customers.
-- These triggers are synthetic and do not evaluate transactions.
INSERT INTO risk.rule_result (
    rule_result_guid, fk_customer_id, fk_rule_id,
    triggered, confidence, risk_points, evaluated_at,
    rule_version, evidence_json, execution_time_ms
)
SELECT
    gen_random_uuid(),
    c.id,
    r.id,
    CASE r.code
        WHEN 'HIGH_VALUE_DEPOSIT' THEN c.id % 3 = 0
        WHEN 'REPEATED_DEPOSIT' THEN c.id % 5 = 0
        WHEN 'HIGH_VALUE_BETTING' THEN c.id % 4 = 0
    END,
    95.00,
    CASE
        WHEN r.code = 'HIGH_VALUE_DEPOSIT'
             AND c.id % 3 = 0 THEN r.risk_weight
        WHEN r.code = 'REPEATED_DEPOSIT'
             AND c.id % 5 = 0 THEN r.risk_weight
        WHEN r.code = 'HIGH_VALUE_BETTING'
             AND c.id % 4 = 0 THEN r.risk_weight
        ELSE 0
    END,
    TIMESTAMP '2026-10-16 00:00:00',
    '1.0',
    jsonb_build_object(
        'source', 'synthetic_demo_seed',
        'validated_transaction_evaluation', FALSE
    ),
    5
FROM (
    SELECT id
    FROM public.customer
    ORDER BY id
    LIMIT 100
) c
CROSS JOIN risk.rules r
WHERE r.code IN (
    'HIGH_VALUE_DEPOSIT',
    'REPEATED_DEPOSIT',
    'HIGH_VALUE_BETTING'
)
AND NOT EXISTS (
    SELECT 1
    FROM risk.rule_result existing
    WHERE existing.fk_customer_id = c.id
      AND existing.fk_rule_id = r.id
      AND existing.evaluated_at = TIMESTAMP '2026-10-16 00:00:00'
      AND existing.rule_version = '1.0'
);


-- 5. Create events for triggered rules.
INSERT INTO risk.risk_event (
    risk_event_guid, fk_customer_id, fk_rule_result_id,
    event_type, severity, status, detected_at
)
SELECT
    gen_random_uuid(),
    rr.fk_customer_id,
    rr.id,
    r.code,
    r.severity,
    'OPEN',
    TIMESTAMP '2026-10-16 00:00:00'
FROM risk.rule_result rr
JOIN risk.rules r ON r.id = rr.fk_rule_id
WHERE rr.triggered = TRUE
  AND rr.evaluated_at = TIMESTAMP '2026-10-16 00:00:00'
  AND NOT EXISTS (
      SELECT 1
      FROM risk.risk_event existing
      WHERE existing.fk_rule_result_id = rr.id
  );


-- 6. Calculate illustrative risk scores from the
-- seeded rule results.
WITH customer_totals AS (
    SELECT
        rr.fk_customer_id,
        SUM(COALESCE(rr.risk_points, 0)) AS total_score
    FROM risk.rule_result rr
    WHERE rr.evaluated_at = TIMESTAMP '2026-10-16 00:00:00'
      AND rr.rule_version = '1.0'
    GROUP BY rr.fk_customer_id
)
INSERT INTO risk.risk_score (
    risk_score_guid, fk_customer_id, score, risk_level,
    scoring_method, model_version, calculated_at
)
SELECT
    gen_random_uuid(),
    ct.fk_customer_id,
    ct.total_score,
    CASE
        WHEN ct.total_score >= 70 THEN 'CRITICAL'
        WHEN ct.total_score >= 50 THEN 'HIGH'
        WHEN ct.total_score >= 25 THEN 'MEDIUM'
        ELSE 'LOW'
    END,
    'RULE_BASED_DEMO',
    'demo-v1',
    TIMESTAMP '2026-10-16 00:00:00'
FROM customer_totals ct
WHERE NOT EXISTS (
    SELECT 1
    FROM risk.risk_score existing
    WHERE existing.fk_customer_id = ct.fk_customer_id
      AND existing.scoring_method = 'RULE_BASED_DEMO'
      AND existing.model_version = 'demo-v1'
      AND existing.calculated_at = TIMESTAMP '2026-10-16 00:00:00'
);


-- 7. Create alerts for high and critical demo scores.
INSERT INTO public.alert (
    alert_guid, fk_customer_id, fk_risk_score_id,
    alert_type, severity, status
)
SELECT
    gen_random_uuid(),
    rs.fk_customer_id,
    rs.id,
    'RULE_BASED_RISK',
    rs.risk_level,
    'OPEN'
FROM risk.risk_score rs
WHERE rs.scoring_method = 'RULE_BASED_DEMO'
  AND rs.model_version = 'demo-v1'
  AND rs.calculated_at = TIMESTAMP '2026-10-16 00:00:00'
  AND rs.risk_level IN ('HIGH', 'CRITICAL')
  AND NOT EXISTS (
      SELECT 1
      FROM public.alert existing
      WHERE existing.fk_risk_score_id = rs.id
  );

COMMIT;
