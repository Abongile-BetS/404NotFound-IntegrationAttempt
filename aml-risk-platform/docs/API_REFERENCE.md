# Additive API

All routes use existing 404NotFound bearer-token validation. The new frontend panels refresh the Keycloak token before calling the extension endpoints.

- `GET /api/v1/intelligence/modules` — module list.
- `GET /api/v1/intelligence/{module}?limit=100` — read-only rows for `aml`, `kyc`, `media`, `screening`, `network`, `rules`, `risk`, `geography` or `reports`.
- `GET /api/v1/intelligence/reports/customer/{customer_id}` — evidence packet, not an AI-generated report.
- `GET /api/v1/intelligence-engine/rules` — the extension's 12 static rule definitions and thresholds.
- `GET /api/v1/intelligence-engine/customers/{customer_id}/evaluate` — on-demand, read-only assessment using financial transactions, recorded screening results, customer data and shared-device links.
- `POST /api/v1/intelligence-engine/simulate` — synthetic payload evaluation; does not write to PostgreSQL.
- `POST /api/v1/intelligence-engine/reports/generate` with `{ "customer_id": "UUID" }` — optional OpenAI-compatible Gemma report from the computed assessment. Returns HTTP 503 when AI endpoint/model is unavailable.

The extension does not persist evaluation results or generated reports. Its rule catalogue endpoint is not a rule editor, and rule definitions in the extension are not wired to the host `risk.rules` parameters or approval versions.

Production requirements: persistent assessments, background reassessment, rule approvals and configuration binding, verified external connectors, access policy and end-to-end testing.
