# Architecture

The React/Vite client calls an authenticated FastAPI REST API. SQLAlchemy and Psycopg 3 persist operational records in PostgreSQL. API services create immutable audit events for security- and compliance-significant actions.

```text
Browser :3061 → FastAPI :8061 → PostgreSQL :5432 (source of truth)
                              ↘ worker queue (planned hardening)
                               ↘ Neo4j projection (planned hardening)
                                ↘ public-source adapters / Gemma (bounded integrations)
```

Risk calculation stores the exact rule version, feature snapshot window, inputs, evidence, score contribution and model version. Rules supplement—not replace—human compliance judgment. Alerts may be generated automatically; formal cases require an analyst by default.

## Neo4j synchronization contract

PostgreSQL owns customer, account, device, payment and IP records. A durable outbox worker should project committed relationship events to Neo4j using idempotency keys. Each batch records source watermark, projected count, failures and retry state. Reconciliation compares PostgreSQL entity/edge counts and sampled hashes with Neo4j. Recovery resets the last confirmed watermark and safely replays idempotent batches. The current slice documents this contract but does not yet ship the worker.

## Security boundaries

Secrets are environment-only. Passwords use Argon2. JWTs are short-lived and role checked server-side. Sensitive identifiers are masked by default. Raw document bytes must be held outside public web roots with content hashes and role-gated download routes. Production requires TLS termination, database encryption/managed disks, secret rotation, rate limiting, malware scanning and backup restore exercises.

