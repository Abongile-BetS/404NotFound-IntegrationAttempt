$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $projectRoot "backend"
$frontend = Join-Path $projectRoot "frontend"
$envFile = Join-Path $projectRoot ".env"
$backendPython = Join-Path $backend ".venv\Scripts\python.exe"

if (-not (Test-Path $envFile)) {
    throw "Missing .env. Run .\scripts\setup-local.ps1 first."
}
if (-not (Test-Path $backendPython)) {
    throw "Backend dependencies are missing. Run .\scripts\setup-local.ps1 first."
}
if (-not (Test-Path (Join-Path $frontend "node_modules"))) {
    throw "Frontend dependencies are missing. Run .\scripts\setup-local.ps1 first."
}
if (Select-String -Path $envFile -Pattern "replace_with_a_strong_password") {
    throw "Replace the password placeholders in .env before starting the application."
}

$postgresPort = 5432
$portEntry = Get-Content $envFile | Where-Object { $_ -match "^POSTGRES_PORT=" } | Select-Object -First 1
if ($portEntry -match "^POSTGRES_PORT=(?<port>\d+)$") {
    $postgresPort = [int]$Matches.port
}

function Test-LocalPort([int]$Port) {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $client.Connect("127.0.0.1", $Port)
        return $true
    }
    catch {
        return $false
    }
    finally {
        $client.Dispose()
    }
}

if (-not (Test-LocalPort $postgresPort)) {
    throw "PostgreSQL is not listening on localhost:$postgresPort. Start PostgreSQL and deploy the schema; see docs\LOCAL_SETUP.md."
}

if (-not (Test-LocalPort 8080)) {
    if (-not $env:KEYCLOAK_HOME) {
        throw "Keycloak is not listening on localhost:8080. Set KEYCLOAK_HOME and follow docs\LOCAL_SETUP.md."
    }

    $keycloakCommand = Join-Path $env:KEYCLOAK_HOME "bin\kc.bat"
    if (-not (Test-Path $keycloakCommand)) {
        throw "KEYCLOAK_HOME does not point to a Keycloak installation."
    }

    $importDirectory = Join-Path $env:KEYCLOAK_HOME "data\import"
    New-Item -ItemType Directory -Force $importDirectory | Out-Null
    Copy-Item (Join-Path $projectRoot "infrastructure\keycloak\aml-risk-realm.json") `
        (Join-Path $importDirectory "aml-risk-realm.json") -Force
    Start-Process -FilePath "powershell.exe" `
        -WorkingDirectory $env:KEYCLOAK_HOME `
        -ArgumentList @(
            "-NoExit",
            "-Command",
            ".\bin\kc.bat start-dev --import-realm --http-port=8080"
        ) | Out-Null

    $deadline = (Get-Date).AddSeconds(60)
    while ((Get-Date) -lt $deadline -and -not (Test-LocalPort 8080)) {
        Start-Sleep -Seconds 2
    }
    if (-not (Test-LocalPort 8080)) {
        throw "Keycloak did not become available on localhost:8080 within 60 seconds."
    }
}

$preflight = @'
from sqlalchemy import create_engine, text
from app.shared.config import get_settings
engine = create_engine(get_settings().database_url)
with engine.connect() as connection:
    customer_table, risk_table = connection.execute(
        text("SELECT to_regclass('public.customer'), to_regclass('risk.risk_score')")
    ).one()
    if customer_table is None or risk_table is None:
        raise SystemExit("Required database schema is missing; follow docs/LOCAL_SETUP.md")
'@
Push-Location $backend
try {
    & $backendPython -c $preflight
    if ($LASTEXITCODE -ne 0) {
        throw "The local database check failed. Verify the POSTGRES_* settings in .env and deploy the schema."
    }
}
finally {
    Pop-Location
}

$backendCommand = "Set-Location -LiteralPath '$backend'; & '.\.venv\Scripts\python.exe' -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
$frontendCommand = "Set-Location -LiteralPath '$frontend'; & npm run dev -- --host 127.0.0.1 --port 5173 --strictPort"

Start-Process -FilePath "powershell.exe" `
    -WorkingDirectory $backend `
    -ArgumentList @("-NoExit", "-Command", $backendCommand) | Out-Null
Start-Process -FilePath "powershell.exe" `
    -WorkingDirectory $frontend `
    -ArgumentList @("-NoExit", "-Command", $frontendCommand) | Out-Null

Write-Host "Started the backend and frontend in separate PowerShell windows."
Write-Host "Frontend: http://localhost:5173"
Write-Host "API docs: http://localhost:8000/docs"
