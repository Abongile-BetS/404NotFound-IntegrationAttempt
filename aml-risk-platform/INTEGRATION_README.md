# 404NotFound additive AML/KYC extension

The original application remains the system of record. The extension adds two authenticated FastAPI routers and embeds its evidence panels into the existing transaction, KYC, screening, network, investigations and executive pages. Existing counterpart pages remain the single destinations; old `/intelligence/*` paths redirect to them. No separate customer database is added.

## Modules
AML Monitoring, KYC/CDD, Adverse Media, PEP & Sanctions, Network Intelligence, Rule Management, AML Risk Evaluation, Geographic Intelligence, and AI Reports. Read views use existing 404NotFound PostgreSQL tables. The added on-demand evaluator runs 12 deterministic checks and calculates an illustrative score; it reads financial transactions, KYC flags, recorded screening results, country and shared-device links. Optional Gemma report generation is available when configured. The extension does not write the assessment or report back to the database.

## Source-code reuse
No external reference implementation is bundled in this repository. The earlier AML-KYC-Enterprise-Risk-Upgrade services, tests and documentation were reference-only because their SQLAlchemy data models differed from 404NotFound's SQL schema; they have been removed during cleanup. The added evaluator uses an explicit adapter for the existing tables rather than replacing the host's customer or risk modules. Keycloak is an external prerequisite; no realm export is bundled in this repository.

## Run locally

Install PostgreSQL, Keycloak, Python and Node.js on the host. Then follow
[`docs/LOCAL_SETUP.md`](docs/LOCAL_SETUP.md) to configure `.env`, create the
database, deploy the schema, import the local Keycloak realm, and start the
backend and frontend in separate terminals. Docker is not used or required.
The local API is available at `http://localhost:8000/docs`; the frontend is
at `http://localhost:5173`. Old `/intelligence/*` paths redirect to their
merged host pages. API details are in `docs/API_REFERENCE.md`.

Optional ETL: install `data/etl/requirements.txt`, then run the ingestion and
normalized-load Python scripts in that order. They use the database settings
from the same `backend/.env`.

## Limitations
- No live external sanctions/PEP/adverse media connector, identity verification, OCR or Iovation integration is added.
- AML rule thresholds and points are static constants; the displayed host rule catalogue does not configure or approve them.
- Assessments and AI reports are not persisted; no background triggers or automatic alert/case creation are added.
- The extension scoring methodology is illustrative and requires compliance approval.
- Native PostgreSQL/Keycloak integration and Gemma inference require validation on a machine with those services installed.
