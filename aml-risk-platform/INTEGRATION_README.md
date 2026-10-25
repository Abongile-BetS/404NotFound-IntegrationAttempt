# 404NotFound additive AML/KYC extension

The original application remains the system of record. The extension adds two authenticated FastAPI routers and embeds its evidence panels into the existing transaction, KYC, screening, network, investigations and executive pages. Existing counterpart pages remain the single destinations; old `/intelligence/*` paths redirect to them. No separate customer database is added.

## Modules
AML Monitoring, KYC/CDD, Adverse Media, PEP & Sanctions, Network Intelligence, Rule Management, AML Risk Evaluation, Geographic Intelligence, and AI Reports. Read views use existing 404NotFound PostgreSQL tables. The added on-demand evaluator runs 12 deterministic checks and calculates an illustrative score; it reads financial transactions, KYC flags, recorded screening results, country and shared-device links. Optional Gemma report generation is available when configured. The extension does not write the assessment or report back to the database.

## Source-code reuse
Relevant AML-KYC-Enterprise-Risk-Upgrade services, tests and documentation are preserved in `integrations/aml_kyc_risk_upgrade_reference/`. They are **reference-only** because their SQLAlchemy data models differ from 404NotFound's SQL schema. The added evaluator uses an explicit adapter for the existing tables rather than replacing the host's customer or risk modules.

## Start
Copy `.env.example` to `.env`, replace every password, then run `docker compose config` and `docker compose up --build -d postgres keycloak-db keycloak backend frontend`. On a new PostgreSQL volume, the included schema deployment script runs automatically. The local `aml-risk` Keycloak realm is imported from `infrastructure/keycloak/aml-risk-realm.json`. Old `/intelligence/*` paths redirect to their merged host pages. API details are in `docs/API_REFERENCE.md`.

## Limitations
- No live external sanctions/PEP/adverse media connector, identity verification, OCR or Iovation integration is added.
- AML rule thresholds and points are static constants; the displayed host rule catalogue does not configure or approve them.
- Assessments and AI reports are not persisted; no background triggers or automatic alert/case creation are added.
- The extension scoring methodology is illustrative and requires compliance approval.
- Docker startup, PostgreSQL/Keycloak integration and Gemma inference still need environment-level validation; this build was not run in Docker here.
