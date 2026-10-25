# AML/KYC extension audit and verification

Audit date: 2026-10-22

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
| Frontend/backend integration | Existing pages contain authenticated evidence panels; redundant intelligence paths redirect to their counterparts. | Source wiring and static configuration were inspected. Production frontend build and live API calls were not verified. |
| Docker deployment | PostgreSQL schema bootstrap for new volumes, Keycloak realm import, environment-based issuer/JWKS/audience, backend and frontend services. Neo4j is excluded. | Compose YAML and realm JSON parse; Docker is not installed in this workspace, so image builds and service startup were not run. |

## Reproducible fixes in this build

- Normalized `backend/requirements.txt` from UTF-16 to UTF-8 so pip can parse it in the backend image.
- Connected the customer assessment to the existing `customer_device` relationship table instead of always marking network evidence unavailable.
- Made malformed timestamps and non-finite transaction amounts safely ignorable in feature calculation.
- Removed inert active-page controls (fake filters, “View All”, graph zoom, add-note and help controls). The executive export button now downloads the displayed rows as CSV; the shared search field remains the working row filter.
- Added local Keycloak realm import and PostgreSQL initialization for a new Docker volume. Existing volumes are not reset or migrated.

## Checks run

| Check | Result |
|---|---|
| Python compileall for backend app | Passed |
| Three focused extension-engine unit tests | Passed |
| Docker Compose YAML parse | Passed |
| Keycloak realm JSON parse | Passed |
| Requirements encoding / no NUL-byte check | Passed |
| Neo4j absent from Compose services | Passed |
| `npm ci` | Blocked: registry returned HTTP 403 for a locked package tarball |
| Frontend production build | Not completed: `tsc` unavailable after dependency installation was blocked |
| Docker Compose config/build/start | Not run: Docker CLI is not installed |
| PostgreSQL integration | Not run: no `psql` client or database service in this workspace |
| Keycloak login/token validation | Not run: no Keycloak service in this workspace |
| Gemma inference | Not run: no configured endpoint/service in this workspace |

## Readiness

This is a locally auditable development integration, not a verified enterprise production AML/KYC system. Before real customer use, implement persistent governed assessments, approved rule configuration/versioning, event-driven reassessment, alert and case creation, live approved screening/identity providers, complete KYC/EDD workflows, production access controls and operational monitoring; then validate the full Docker/PostgreSQL/Keycloak/Gemma flow and frontend behavior in the target environment.
