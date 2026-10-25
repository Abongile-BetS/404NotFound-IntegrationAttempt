\set ON_ERROR_STOP on

\echo '========================================'
\echo 'Creating Schemas'
\echo '========================================'

\i /tmp/db_setup/001_schemas.sql

\echo '========================================'
\echo 'Creating Customer Domain'
\echo '========================================'

\i /tmp/db_setup/002_customer.sql
\i /tmp/db_setup/003_account.sql
\i /tmp/db_setup/004_customer_transaction_type.sql
\i /tmp/db_setup/i004_customer_transaction_type.sql
\i /tmp/db_setup/005_financial_transaction.sql
\i /tmp/db_setup/019_bet.sql
\i /tmp/db_setup/020_bet_transaction.sql
\i /tmp/db_setup/021_customer_onboarding.sql
\i /tmp/db_setup/022_customer_identity_document.sql

\echo '========================================'
\echo 'Creating KYC and Screening Domain'
\echo '========================================'

\i /tmp/db_setup/006_kyc_record.sql
\i /tmp/db_setup/007_screening_result.sql

\echo '========================================'
\echo 'Creating Network Intelligence Domain'
\echo '========================================'

\i /tmp/db_setup/008_device.sql
\i /tmp/db_setup/009_customer_device.sql
\i /tmp/db_setup/010_iovation_event.sql

\echo '========================================'
\echo 'Creating Raw Data Layer'
\echo '========================================'

\i /tmp/db_setup/011_raw_iovation.sql

\echo '========================================'
\echo 'Creating Rule Engine'
\echo '========================================'

\i /tmp/db_setup/012_rules.sql
\i /tmp/db_setup/013_rule_parameter.sql
\i /tmp/db_setup/014_rule_version.sql
\i /tmp/db_setup/015_rule_result.sql

\echo '========================================'
\echo 'Creating Risk Engine'
\echo '========================================'

\i /tmp/db_setup/016_risk_event.sql
\i /tmp/db_setup/017_risk_score.sql

\echo '========================================'
\echo 'Creating Alerting Layer'
\echo '========================================'

\i /tmp/db_setup/018_alert.sql

\echo '========================================'
\echo 'Inserting Data And Making db_setup Changes'
\echo '========================================'

\i /tmp/db_setup/i005_financial_transaction.sql
\i /tmp/db_setup/i006_kyc_record.sql
\i /tmp/db_setup/i019_bet.sql
\i /tmp/db_setup/dml020_bet.sql
\i /tmp/db_setup/i020_bet_transaction.sql
\i /tmp/db_setup/i021a_customer_onboarding.sql
\i /tmp/db_setup/i021b_customer_onboarding.sql



\echo '========================================'
\echo 'DATABASE DEPLOYMENT COMPLETED'
\echo '========================================'