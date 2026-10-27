# Additive API

All `/api/v1` routes require a valid Keycloak bearer token; `/` and `/health` remain public. The frontend refreshes tokens before API calls, and protected application pages redirect unauthenticated users to sign in.

- Existing list routes remain under `/api/v1` and preserve array response shapes. Customers, KYC, alerts, transactions and screening accept `limit` (1-500, default 100) and `offset` (default 0). The intelligence module list uses the same parameters and returns the current page in `rows`.
- `GET /api/v1/intelligence/modules` — module list.
- `GET /api/v1/intelligence/{module}?limit=100&offset=0` — read-only rows for `aml`, `kyc`, `media`, `screening`, `network`, `rules`, `risk`, `geography` or `reports`.
- `GET /api/v1/intelligence/reports/customer/{customer_id}` — evidence packet, not an AI-generated report.
- `GET /api/v1/intelligence-engine/rules` — the extension's 12 static rule definitions and thresholds.
- `GET /api/v1/intelligence-engine/customers/{customer_id}/evaluate` — on-demand, read-only assessment using financial transactions, recorded screening results, customer data and shared-device links.
- `POST /api/v1/intelligence-engine/simulate` — synthetic payload evaluation; does not write to PostgreSQL.
- `POST /api/v1/intelligence-engine/reports/generate` with `{ "customer_id": "UUID" }` — optional OpenAI-compatible Gemma report from the computed assessment. Returns HTTP 503 when AI endpoint/model is unavailable.

The extension does not persist evaluation results or generated reports. Its rule catalogue endpoint is not a rule editor, and rule definitions in the extension are not wired to the host `risk.rules` parameters or approval versions.

Production requirements: persistent assessments, background reassessment, rule approvals and configuration binding, verified external connectors, access policy and end-to-end testing.

Sensitive API responses are marked `Cache-Control: no-store`. Configure
distributed rate limiting, HTTPS, HSTS, and other deployment security headers
at the trusted production proxy or API gateway; the local development server
does not terminate HTTPS or provide distributed rate limiting.
