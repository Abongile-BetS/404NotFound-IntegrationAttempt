$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $projectRoot "backend"
$frontend = Join-Path $projectRoot "frontend"
$python = Get-Command python -ErrorAction SilentlyContinue
$npm = Get-Command npm -ErrorAction SilentlyContinue

if (-not $python) {
    throw "Python 3.12 or newer is required. Install Python and try again."
}
if (-not $npm) {
    throw "Node.js and npm are required. Install Node.js and try again."
}

$pythonVersionText = & python --version
if ($pythonVersionText -notmatch "Python (?<version>\d+\.\d+)") {
    throw "Unable to determine the installed Python version."
}
if ([version]$Matches.version -lt [version]"3.12") {
    throw "Python 3.12 or newer is required. Found $pythonVersionText."
}

$nodeVersionText = & node --version
if ($nodeVersionText -notmatch "^v(?<version>\d+)") {
    throw "Unable to determine the installed Node.js version."
}
if ([int]$Matches.version -lt 24) {
    throw "Node.js 24 or newer is required. Found $nodeVersionText."
}

$envFile = Join-Path $backend ".env"
if (-not (Test-Path $envFile)) {
    Copy-Item (Join-Path $backend ".env.example") $envFile
    Write-Host "Created .env from .env.example."
}

$frontendEnvFile = Join-Path $frontend ".env"
if (-not (Test-Path $frontendEnvFile)) {
    Copy-Item (Join-Path $frontend ".env.example") $frontendEnvFile
}

# Enable local development auth bypass when Keycloak is not configured.
if (-not $env:KEYCLOAK_HOME -and -not (Test-NetConnection -ComputerName 127.0.0.1 -Port 8080 -InformationLevel Quiet -WarningAction SilentlyContinue)) {
    if (Select-String -Path $envFile -Pattern "^DEV_AUTH_BYPASS=" -Quiet) {
        (Get-Content $envFile) -replace "^DEV_AUTH_BYPASS=.*", "DEV_AUTH_BYPASS=true" | Set-Content $envFile
    } else {
        Add-Content $envFile "DEV_AUTH_BYPASS=true"
    }
    if (Select-String -Path $frontendEnvFile -Pattern "^VITE_DEV_AUTH_BYPASS=" -Quiet) {
        (Get-Content $frontendEnvFile) -replace "^VITE_DEV_AUTH_BYPASS=.*", "VITE_DEV_AUTH_BYPASS=true" | Set-Content $frontendEnvFile
    } else {
        Add-Content $frontendEnvFile "VITE_DEV_AUTH_BYPASS=true"
    }
    Write-Host "Keycloak was not detected; enabled local development auth bypass."
}

Push-Location $backend
try {
    if (-not (Test-Path ".venv\Scripts\python.exe")) {
        & python -m venv .venv
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create the backend virtual environment."
        }
    }
    & .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install backend dependencies."
    }
    & .\.venv\Scripts\python.exe -m pip install -r ..\data\etl\requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install ETL dependencies."
    }
}
finally {
    Pop-Location
}

Push-Location $frontend
try {
    & npm ci
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install frontend dependencies."
    }
}
finally {
    Pop-Location
}

Write-Host "App dependencies are installed. Configure .env if needed; PostgreSQL and Keycloak are optional because the app can use embedded PostgreSQL and dev auth bypass. Then run .\scripts\run-local.ps1."
