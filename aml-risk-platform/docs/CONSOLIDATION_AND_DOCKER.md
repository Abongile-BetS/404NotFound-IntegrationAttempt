# 404NotFound consolidation and Docker guide

## Scope
Existing counterpart pages are retained. Additional evidence panels are embedded in KYC, screening, transactions, network, investigations and executive pages. Generic `/intelligence/*` bookmarks redirect to the corresponding existing screen. The existing authenticated intelligence endpoints remain available for these panels. Navigation is grouped by Overview, Customer compliance, Detection & intelligence and Operations.

## No Neo4j container
Neo4j is intentionally **not** in docker-compose. Network intelligence currently reads customer-device relationships from PostgreSQL. External Neo4j connectivity, if needed, must be configured separately.

## Start (development only)
1. From `aml-risk-platform`, copy `.env.example` to `.env` and replace all three passwords. Use URL-safe characters for `POSTGRES_PASSWORD`, which is included in the backend database URL. Never commit `.env`.
2. Ensure Docker Desktop is running.
3. Run `docker compose config --quiet` to validate environment interpolation.
4. Run `docker compose up --build -d` to start PostgreSQL, Keycloak, the backend and frontend.
5. The local Keycloak realm `aml-risk` and public client `aml-frontend` are imported from `infrastructure/keycloak/aml-risk-realm.json`. Create a user through the local Keycloak registration page after startup.
6. On a **new** Docker PostgreSQL volume, the SQL schema deploy script runs automatically. Existing volumes are not reset or migrated by this compose setup; apply schema changes through your normal database change process.
7. Open `http://localhost:5173`, backend docs at `http://localhost:8000/docs`, and Keycloak at `http://localhost:8080`.

The root `.env` is the only environment file used by Docker Compose. Frontend `VITE_*` settings are supplied as build arguments; rebuild the frontend after changing them. The frontend `.env.example` is only for running Vite outside Docker.

Optional ETL profile: `docker compose --profile etl run --rm etl-engine`. This one-shot job uses the same PostgreSQL credentials and mounts the included iovation demo seed data.

## Environment variables
The Compose `.env` is used for interpolation and server secrets, including the public Keycloak issuer, container-reachable JWKS URL and API audience. The frontend Vite settings are embedded at **build time**. Rebuild frontend when changing VITE_* settings. The optional AI endpoint must be reachable from the backend container; `localhost` inside Docker is not your host machine. AI reports return unavailable if no endpoint/model is configured.

## Limitations
No live production credentials are bundled. This remains a local development deployment (`start-dev`, HTTP, public SPA client), not a production security configuration. PostgreSQL, Keycloak and Gemma end-to-end flows require validation in the deployment environment. Live adverse-media and sanctions-provider retrieval, approved identity verification, persistent assessments, automatic event triggers and production authorization policies are not part of this extension.
