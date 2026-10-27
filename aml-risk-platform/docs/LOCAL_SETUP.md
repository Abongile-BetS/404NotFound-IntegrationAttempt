# Local development setup

The backend and frontend run directly on your computer. PostgreSQL and
Keycloak are external local prerequisites; this repository does not include
Docker configuration or install those services.

## Prerequisites

- Windows 10/11 with PowerShell
- Python 3.12 or newer
- Node.js 24 or newer
- PostgreSQL 17, with the PostgreSQL command-line tools (`psql`, `createdb`)
- A compatible Keycloak 26 distribution and its required Java runtime

## Configure the database

1. Start the PostgreSQL Windows service.
2. Create a local role and database using pgAdmin or `psql`. For example, in
   PowerShell, replace the sample password with your own URL-safe password:

   ```powershell
   psql -U postgres -c "CREATE ROLE aml LOGIN PASSWORD 'change_this_password';"
   createdb -U postgres -O aml aml
   ```

3. From `aml-risk-platform`, copy and edit the environment example:

   ```powershell
   Copy-Item .\backend\.env.example .\backend\.env
   ```

   Set `POSTGRES_PASSWORD` to the credential you chose. The backend builds its
   database URL safely from these shared PostgreSQL settings, so you do not
   need to maintain a separate database URL or duplicate password. Set
   `POSTGRES_PORT` if your local PostgreSQL uses a non-default port.

4. Apply the schema once to a newly created database:

   ```powershell
   psql -h localhost -p 5432 -U aml -d aml -v ON_ERROR_STOP=1 -f .\data\db\db_setup\deploy.sql
   ```

   Replace `5432` if you changed `POSTGRES_PORT`. Do not rerun the data inserts
   against a database that already contains data without reviewing the SQL
   first.

## Configure local Keycloak

1. Download and extract Keycloak 26. Set `KEYCLOAK_HOME` to the extracted
   directory in PowerShell:

   ```powershell
   $env:KEYCLOAK_HOME = "C:\path\to\keycloak"
   ```

2. Start Keycloak in development mode from a separate terminal:

   ```powershell
   Set-Location $env:KEYCLOAK_HOME
   .\bin\kc.bat start-dev --http-port=8080
   ```

   The realm configures the `aml-risk` realm and the public `aml-frontend`
   client for `http://localhost:5173`. This HTTP development configuration is
   not suitable for production.

## Install and run the app

From the repository's `aml-risk-platform` directory, the setup script creates
the virtual environment, installs backend/frontend dependencies and creates
`.env` from the example if needed:

```powershell
.\scripts\setup-local.ps1
```

Edit `.env` before starting. Start PostgreSQL and make sure its schema is
deployed. Set `$env:KEYCLOAK_HOME` to your Keycloak installation if you want
the run script to import the realm and start Keycloak for you. Then run:

```powershell
.\scripts\run-local.ps1
```

The run script verifies the local database and required schema, starts
Keycloak when `KEYCLOAK_HOME` is set and Keycloak is not already listening,
then launches the backend and frontend in separate PowerShell windows.

To start services manually instead, use two terminals. In the first:

```powershell
Set-Location .\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

In the second, from the `aml-risk-platform` directory:

```powershell
Set-Location .\frontend
npm run dev -- --host 127.0.0.1
```

Open:

- Frontend: `http://localhost:5173`
- API documentation: `http://localhost:8000/docs`
- Keycloak: `http://localhost:8080`

The backend reads the `backend/.env` regardless of its current working directory.
The frontend uses the local defaults in `frontend/.env.example`; copy that file
to `frontend/.env.local` only if you need to change its Vite settings.
The backend uses SQLAlchemy 2.x Core with a pooled PostgreSQL engine and
parameterized SQL. The ETL scripts use psycopg directly for their batch-loading
workflows.

## Optional ETL

The ETL scripts load the `backend/.env` automatically. Install their dependencies
and run them from the platform root:

```powershell
python -m pip install -r .\data\etl\requirements.txt
python .\data\etl\src\ingestion.py
python .\data\etl\src\normalized_load.py
```

Ingestion reads `data/db/seed/iovation_demo_synthetic_100.csv`. It requires the
database schema to be deployed first.

## Operational notes

- Every `/api/v1` route requires a valid Keycloak bearer token. The frontend
  redirects unauthenticated users to sign in; `/` and `/health` are public.
- `GET` list endpoints accept `limit` (1-500, default 100) and `offset`
  (default 0). Existing endpoints and array response shapes are preserved.
- AML/customer API responses use `Cache-Control: no-store`; do not enable
  shared caching for these records.
- API request log payloads are JSON and include route templates, status codes,
  elapsed time, and a generated request ID. They do not log request bodies or
  tokens.
- For production, terminate HTTPS and configure distributed rate limiting,
  security headers, and log retention at the trusted reverse proxy or API
  gateway. This local development setup is not a production deployment.

## Code quality checks

The setup script installs Ruff for Python linting and formatting. From the
`aml-risk-platform` directory, run:

```powershell
.\backend\.venv\Scripts\ruff.exe check .\backend\app .\data\etl\src
.\backend\.venv\Scripts\ruff.exe format --check .\backend\app .\data\etl\src
Set-Location .\backend
.\.venv\Scripts\python.exe -m unittest discover -s app\tests
Set-Location ..\frontend
npm run build
npm run lint
```
