# Risk engine upgrade notes (2026-10-21)

## Implemented
- `backend/app/services/risk.py`: rule evaluators now consume approved database configuration values, selecting the latest enabled and approved rule version by code.
- Corrected `LOW_WAGER_WITHDRAW` to use seven-day wagering-to-deposit ratio, rather than withdrawal-to-deposit ratio. Assumes wagering transactions have `kind='bet'` in the transaction table.
- When no wagering transactions exist, the low-wagering rule is marked `unavailable` (the current schema cannot prove whether the customer placed no bets or the feed is missing).
- Behavioural feature builder supports an `as_of` timestamp, 1/7/30/90-day windows, prior 30-day baseline, and deposit growth with missing-baseline flag.
- Rule executions preserve evaluated/unavailable status, threshold and observed data, and risk assessments include coverage and unavailable-rule identifiers.
- Four new regression tests in `backend/tests/test_risk_engine_v2.py`.

## Known limitations and requirements before production
- This is a targeted backend improvement, **not** a complete enterprise certification or a full redesign of the frontend.
- Only the four existing default rules have evaluators; a 30-rule AML catalogue has NOT been implemented.
- No external identity verification, Iovation, automated document OCR, live screening provider, or production job orchestration was added.
- The scoring methodology remains an additive prototype, and compliance must approve thresholds and actions.
- Source coverage cannot be established reliably from an absence of wagering records. Implement explicit ingestion/feed-health status to distinguish missing feed from genuine zero wagering.
- The current `RuleExecution` table has no dedicated `execution_status` column; status is stored in JSON evidence.
- The `RiskAssessment.confidence` field is temporarily used for coverage fraction; it is **not** a statistical probability of suspicious behaviour.
- Existing model includes `risk_score=0` default; clients should use `components.assessment_status` and `unavailable_rules` rather than assuming zero means cleared.
- Reassessments still run synchronously and may create multiple feature snapshots; a durable worker and idempotency scheme are required.
- Ensure new customers and transaction imports trigger a durable reassessment process; existing import endpoints may require follow-up changes.
- PostgreSQL, frontend, external service and end-to-end tests were not run in this environment.

## Test results
`DATABASE_URL=sqlite+pysqlite:///:memory: python -m pytest -q tests/test_risk_engine_v2.py tests/test_identity.py tests/test_risk_logic.py tests/test_kyc_contract.py` => 9 passed.
Full suite blocked by missing local `feedparser` and `truststore` packages in build environment.

## Windows setup
See existing README and `.env.example`. Never use an included production secret; this ZIP excludes the uploaded `.env` and local data. Create your own `.env` with PostgreSQL credentials and secrets.
