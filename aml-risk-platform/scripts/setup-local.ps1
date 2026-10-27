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

$envFile = Join-Path $projectRoot ".env"
if (-not (Test-Path $envFile)) {
    Copy-Item (Join-Path $projectRoot ".env.example") $envFile
    Write-Host "Created .env from .env.example. Edit it with your local database credentials before starting the app."
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

Write-Host "App dependencies are installed. Install/start PostgreSQL and Keycloak, configure .env, and then run .\scripts\run-local.ps1."
