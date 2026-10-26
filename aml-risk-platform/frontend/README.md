# Frontend

The React/TypeScript frontend uses Vite for local development and calls the
FastAPI service at `http://localhost:8000`. Keycloak is configured by the
`VITE_KEYCLOAK_*` values in `.env.local`; the defaults are in `.env.example`.

From the `aml-risk-platform` directory:

```powershell
Set-Location .\frontend
npm ci
npm run dev -- --host 127.0.0.1
```

For a production bundle, run `npm run build`. The development server is
available at `http://localhost:5173`. See
[`../docs/LOCAL_SETUP.md`](../docs/LOCAL_SETUP.md) for PostgreSQL, Keycloak,
backend and complete application setup.
