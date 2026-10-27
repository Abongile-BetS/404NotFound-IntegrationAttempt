$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $projectRoot "backend"
$frontend = Join-Path $projectRoot "frontend"
$envFile = Join-Path $backend ".env"
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
# Password placeholders are allowed; the backend falls back to embedded PostgreSQL
# when the configured PostgreSQL server is unavailable.
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

# PostgreSQL is optional: the backend falls back to an embedded PostgreSQL instance
# when a configured PostgreSQL server is unavailable.
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
