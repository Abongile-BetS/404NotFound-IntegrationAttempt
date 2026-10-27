# AML/KYC extension audit and verification

Audit date: 2026-10-26

This report describes the latest local build. “Verified” means the specific check listed below ran in this workspace; it does not imply production readiness.

## Module status

| Requested area | What is wired | Verified status / remaining gap |
|---|---|---|
| AML monitoring | Financial transactions feed 12 deterministic checks and an on-demand assessment endpoint. | Engine unit tests pass. It does not persist results, run on events, analyze transaction sequences, or create alerts/cases. |
| KYC/CDD | Existing customer and latest KYC record are shown; incomplete FICA evidence can trigger a check. | Read integration is implemented; this is not automated identity verification, document OCR, complete CDD/EDD, or a workflow editor. |
| Adverse media | Existing media screening records are shown and included as candidate signals. | No live public-source search or article retrieval is connected. No hit or unavailable source is not a clear result. |
| PEP & sanctions | Existing PEP/sanctions screening records are shown and candidate matches can trigger signals. | No live list provider, alias screening, identity matching or analyst disposition workflow is connected. |
| Network intelligence | Shared-device PostgreSQL relationships appear in the network view and feed a one-hop linked-customer check. | SQL integration and rule input are implemented; no multi-hop graph or Neo4j service is included. |
| Rule management | Existing `risk.rules` records are displayed in the merged investigations/risk page. | Read-only. Extension thresholds/weights are static; there is no edit, approval, activation or history workflow. |
| AML risk evaluation | On-demand 0–100 additive score with per-rule status, evidence and unavailable coverage. | Pure engine behavior is unit-tested. The score is illustrative, not persisted and not the host platform's official score. |
| Geographic intelligence | Customer country distribution and missing-country check. | Implemented as a basic field check; no jurisdiction risk catalogue or location velocity analysis. |
| AI reports | Optional OpenAI-compatible Gemma endpoint receives assessment features and returns report text. | Request path and failure handling are implemented; live inference is unverified and requires `AI_BASE_URL`, `AI_MODEL_NAME`, network access and a valid service. Reports are not stored. |
| Alerts & investigations | Existing 404NotFound pages and APIs remain the operational counterparts. | The extension does not automatically create or assign alerts/cases; API workflows were not exercised against a live database. |
| Frontend/backend integration | All `/api/v1` routes require Keycloak bearer authentication; application pages are protected and API calls refresh/attach the token. Redundant intelligence paths redirect to their counterparts. | Frontend build/lint and backend auth smoke tests pass; live API calls were not verified. |
| Local deployment | Host PostgreSQL and Keycloak with the FastAPI backend and Vite frontend. Neo4j is excluded. | Setup instructions are in `docs/LOCAL_SETUP.md`; live PostgreSQL/Keycloak integration has not been run in this workspace. |

## Reproducible fixes in this build

- Normalized `backend/requirements.txt` from UTF-16 to UTF-8 so pip can parse it during local setup.
- Connected the customer assessment to the existing `customer_device` relationship table instead of always marking network evidence unavailable.
- Made malformed timestamps and non-finite transaction amounts safely ignorable in feature calculation.
- Removed inert active-page controls (fake filters, “View All”, graph zoom, add-note and help controls). The executive export button now downloads the displayed rows as CSV; the shared search field remains the working row filter.
- Added local Keycloak realm import and a portable PostgreSQL schema deployment script using paths relative to the script.
- Added bounded list pagination, no-store API response headers, request IDs and structured request logs.
- Protected all versioned API routes with bearer-token validation and connected frontend requests to Keycloak token refresh.
- Removed Docker configuration; the app now runs directly on the host.

## Checks run

| Check | Result |
|---|---|
| Python compileall for backend app | Passed |
| Backend unit tests (`python -m unittest discover -s app/tests`) | Passed (7 tests) |
| Keycloak realm JSON parse | Passed |
| Requirements encoding / no NUL-byte check | Passed |
| Frontend production build | Passed |
| Frontend lint | Passed |
| Frontend dependency audit | Passed; zero vulnerabilities reported |
| PostgreSQL integration | Not run: PostgreSQL/`psql` are unavailable in this workspace |
| Keycloak login/token validation | Not run: no local Keycloak service in this workspace |
| Gemma inference | Not run: no configured endpoint/service in this workspace |

## Readiness

This is a locally auditable development integration, not a verified enterprise production AML/KYC system. Before real customer use, implement persistent governed assessments, approved rule configuration/versioning, event-driven reassessment, alert and case creation, live approved screening/identity providers, complete KYC/EDD workflows, production access controls and operational monitoring; then validate the PostgreSQL/Keycloak/Gemma flow and frontend behavior in the target environment.
