\set ON_ERROR_STOP on

\echo '========================================'
\echo 'Creating Schemas'
\echo '========================================'

\ir 001_schemas.sql

\echo '========================================'
\echo 'Creating Customer Domain'
\echo '========================================'

\ir 002_customer.sql
\ir 003_account.sql
\ir 004_customer_transaction_type.sql
\ir i004_customer_transaction_type.sql
\ir 005_financial_transaction.sql
\ir 019_bet.sql
\ir 020_bet_transaction.sql
\ir 021_customer_onboarding.sql
\ir 022_customer_identity_document.sql

\echo '========================================'
\echo 'Creating KYC and Screening Domain'
\echo '========================================'

\ir 006_kyc_record.sql
\ir 007_screening_result.sql

\echo '========================================'
\echo 'Creating Network Intelligence Domain'
\echo '========================================'

\ir 008_device.sql
\ir 009_customer_device.sql
\ir 010_iovation_event.sql

\echo '========================================'
\echo 'Creating Raw Data Layer'
\echo '========================================'

\ir 011_raw_iovation.sql

\echo '========================================'
\echo 'Creating Rule Engine'
\echo '========================================'

\ir 012_rules.sql
\ir 013_rule_parameter.sql
\ir 014_rule_version.sql
\ir 015_rule_result.sql

\echo '========================================'
\echo 'Creating Risk Engine'
\echo '========================================'

\ir 016_risk_event.sql
\ir 017_risk_score.sql

\echo '========================================'
\echo 'Creating Alerting Layer'
\echo '========================================'

\ir 018_alert.sql

\echo '========================================'
\echo 'Inserting Data And Making db_setup Changes'
\echo '========================================'

\ir i005_financial_transaction.sql
\ir i006_kyc_record.sql
\ir i019_bet.sql
\ir dml020_bet.sql
\ir i020_bet_transaction.sql
\ir i021a_customer_onboarding.sql
\ir i021b_customer_onboarding.sql



\echo '========================================'
\echo 'Creating Investigation Case Layer'
\echo '========================================'

\ir 023_investigation_case.sql

\echo '========================================'
\echo 'DATABASE DEPLOYMENT COMPLETED'
\echo '========================================'