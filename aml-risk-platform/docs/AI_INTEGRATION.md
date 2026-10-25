# AI / Gemma integration

Set `AI_BASE_URL` (OpenAI-compatible `/v1` URL), `AI_MODEL_NAME`, and `AI_API_KEY` in backend environment. POST `/api/v1/intelligence-engine/reports/generate` with `{ "customer_id": "UUID" }` requires the existing authentication and generates a report from computed assessment evidence. It fails closed with HTTP 503 if unavailable. It does not store generated reports and does not submit full identity details. Validate privacy and network permissions before enabling.
