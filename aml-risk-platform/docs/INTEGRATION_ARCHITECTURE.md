# 404NotFound additive integration

The extension uses the existing application as the host and places AML/KYC evidence panels inside the existing transaction, KYC, screening, network, investigation and executive pages. Old `/intelligence/*` bookmarks redirect to these counterparts. No separate generic intelligence page or parallel customer database is introduced.

The two additive FastAPI routers read the host PostgreSQL tables. The evaluator calculates an on-demand score from its 12 deterministic checks; it does not replace the existing stored scoring service. The frontend uses the existing Keycloak token and API base configuration. Docker Compose imports a local Keycloak realm and deploys the SQL schema on a new PostgreSQL volume. Neo4j is not included.

**Limitations**: no PEP/sanctions provider, live adverse-media retrieval, Iovation, OCR, identity verification, EDD workflow, background assessment writes, alert/case creation from extension findings, or approved production scoring methodology. Never interpret absent data as no adverse media or no sanctions.
