[CmdletBinding()]
param(
    [switch]$NoBrowser,
    [ValidateRange(5, 120)][int]$TimeoutSeconds = 45
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$rootPath = [IO.Path]::GetFullPath($PSScriptRoot)
$pythonPath = Join-Path $rootPath '.venv\Scripts\python.exe'
$runtimePath = Join-Path $rootPath 'runtime'
$recordPath = Join-Path $runtimePath 'server.json'
$consoleUrl = 'http://127.0.0.1:8765'
$statusUrl = "$consoleUrl/control/status"

function Test-SamePath([string]$Left, [string]$Right) {
    if (-not $Left -or -not $Right) { return $false }
    return [string]::Equals(
        [IO.Path]::GetFullPath($Left).TrimEnd('\', '/'),
        [IO.Path]::GetFullPath($Right).TrimEnd('\', '/'),
        [StringComparison]::OrdinalIgnoreCase
    )
}

function Get-ExpectedBasePython {
    $configPath = Join-Path $rootPath '.venv\pyvenv.cfg'
    $venvHome = $null
    foreach ($line in (Get-Content -LiteralPath $configPath -Encoding UTF8)) {
        if ($line -match '^\s*home\s*=\s*(.+?)\s*$') { $venvHome = $Matches[1]; break }
    }
    if (-not $venvHome -or -not [IO.Path]::IsPathRooted($venvHome)) {
        throw 'Cannot establish the base Python path from .venv/pyvenv.cfg.'
    }
    $expectedPath = [IO.Path]::GetFullPath((Join-Path $venvHome 'python.exe'))
    if (-not (Test-Path -LiteralPath $expectedPath -PathType Leaf)) {
        throw 'The base Python named by .venv/pyvenv.cfg is missing.'
    }
    return $expectedPath
}

function Get-ConsoleStatus {
    try {
        # Windows PowerShell 5.1 can decode a JSON body without charset as
        # ANSI. Decode the raw UTF-8 bytes explicitly so Chinese paths match.
        $response = Invoke-WebRequest -Uri $statusUrl -TimeoutSec 2 -Method Get -UseBasicParsing
        if ($response.RawContentStream.CanSeek) { $response.RawContentStream.Position = 0 }
        $reader = [IO.StreamReader]::new($response.RawContentStream, [Text.Encoding]::UTF8)
        try { return ($reader.ReadToEnd() | ConvertFrom-Json) }
        finally { $reader.Dispose() }
    } catch {
        return $null
    }
}

function Get-VerifiedProcess($health) {
    if ($null -eq $health -or $health.project -ne 'agent-control-console') {
        throw 'Port 8765 is not serving this project. No process has been stopped.'
    }
    if (-not (Test-SamePath ([string]$health.root) $rootPath) -or
        -not (Test-SamePath ([string]$health.python_executable) $pythonPath)) {
        throw 'The live project root or virtual environment does not match this installation.'
    }
    $serverProcessId = 0
    if (-not [int]::TryParse([string]$health.pid, [ref]$serverProcessId) -or $serverProcessId -le 0) {
        throw 'The health response contains no valid process ID.'
    }
    $serverProcess = Get-Process -Id $serverProcessId -ErrorAction Stop
    $expectedBasePython = Get-ExpectedBasePython
    $directVenvProcess = Test-SamePath $serverProcess.Path $pythonPath
    $verifiedBaseProcess = (Test-SamePath $serverProcess.Path $expectedBasePython) -and
        (Test-SamePath ([string]$health.python_base_executable) $expectedBasePython)
    if (-not $directVenvProcess -and -not $verifiedBaseProcess) {
        throw 'The running service does not use this project virtual environment. Refusing to adopt it.'
    }
    return $serverProcess
}

function Write-ServerRecord($serverProcess, $health, [int]$LauncherProcessId = 0) {
    $record = [ordered]@{
        project = 'agent-control-console'
        root = $rootPath
        pid = $serverProcess.Id
        launcher_pid = $(if ($LauncherProcessId -gt 0 -and $LauncherProcessId -ne $serverProcess.Id) { $LauncherProcessId } else { $null })
        python_path = $pythonPath
        process_path = $serverProcess.Path
        python_base_path = Get-ExpectedBasePython
        process_start_utc = $serverProcess.StartTime.ToUniversalTime().ToString('o')
        recorded_at = [DateTime]::UtcNow.ToString('o')
        url = $consoleUrl
        upstream_commit = $health.upstream_commit
        version = $health.version
    }
    $record | ConvertTo-Json | Set-Content -LiteralPath $recordPath -Encoding UTF8
}

try {
    if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
        throw 'The virtual environment is missing. Run install.ps1 first.'
    }
    $frontendIndex = Join-Path $rootPath 'agentscope\examples\web_ui\frontend\dist\index.html'
    if (-not (Test-Path -LiteralPath $frontendIndex -PathType Leaf)) {
        throw 'The frontend build is missing. Run install.ps1 first.'
    }
    if (-not (Test-Path -LiteralPath (Join-Path $rootPath 'control\main.py') -PathType Leaf)) {
        throw 'control/main.py is missing. Restore the complete project before starting.'
    }
    New-Item -ItemType Directory -Path $runtimePath -Force | Out-Null
    $taskTempPath = Join-Path $rootPath '.cache\tmp'
    $pipCachePath = Join-Path $rootPath '.cache\pip'
    New-Item -ItemType Directory -Path $taskTempPath, $pipCachePath -Force | Out-Null
    $env:TEMP = $taskTempPath
    $env:TMP = $taskTempPath
    $env:PIP_CACHE_DIR = $pipCachePath
    $env:AGENT_CONSOLE_PORT = '8765'
    $env:PYTHONUTF8 = '1'
    $env:PYTHONIOENCODING = 'utf-8'

    $existingHealth = Get-ConsoleStatus
    if ($null -ne $existingHealth) {
        $existingProcess = Get-VerifiedProcess $existingHealth
        Write-ServerRecord $existingProcess $existingHealth
        Write-Host "Already running: $consoleUrl (PID $($existingProcess.Id))"
        if (-not $NoBrowser) { Start-Process -FilePath $consoleUrl }
        exit 0
    }

    $occupied = @([Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties().GetActiveTcpListeners() |
        Where-Object { $_.Port -eq 8765 })
    if ($occupied.Count -gt 0) {
        throw 'Port 8765 is occupied but the project health check failed. No process has been stopped.'
    }

    $launcherProcess = Start-Process -FilePath $pythonPath -ArgumentList @('-u', '-m', 'control.main') `
        -WorkingDirectory $rootPath -WindowStyle Hidden -PassThru `
        -RedirectStandardOutput (Join-Path $runtimePath 'server.stdout.log') `
        -RedirectStandardError (Join-Path $runtimePath 'server.stderr.log')
    # Save ownership immediately, even when startup later fails. A stop still
    # requires a live matching health response before it may terminate anything.
    Write-ServerRecord $launcherProcess ([pscustomobject]@{ upstream_commit = ''; version = '' })
    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    do {
        $health = Get-ConsoleStatus
        if ($null -ne $health) {
            $verifiedProcess = Get-VerifiedProcess $health
            $startedByLauncher = $verifiedProcess.Id -eq $launcherProcess.Id -or
                [int]$health.parent_pid -eq $launcherProcess.Id
            if (-not $startedByLauncher -or
                $verifiedProcess.StartTime.ToUniversalTime() -lt $launcherProcess.StartTime.ToUniversalTime().AddSeconds(-1)) {
                throw 'Another process answered during startup. Refusing to change either process.'
            }
            # Windows venv python.exe can be a launcher whose child is the
            # actual server. Record and later stop only the verified child.
            Write-ServerRecord $verifiedProcess $health $launcherProcess.Id
            Write-Host "Started: $consoleUrl (PID $($verifiedProcess.Id))"
            Write-Host 'Model inference requires a configured model. External platform adapters are separate.'
            if (-not $NoBrowser) { Start-Process -FilePath $consoleUrl }
            exit 0
        }
        $launcherProcess.Refresh()
        if ($launcherProcess.HasExited) {
            throw "The launcher exited with code $($launcherProcess.ExitCode). See runtime/server.stderr.log."
        }
        Start-Sleep -Milliseconds 500
    } while ([DateTime]::UtcNow -lt $deadline)
    throw 'Startup timed out. Inspect runtime/server.stderr.log and server.stdout.log. The process was not forcibly stopped.'
} catch {
    Write-Error $_ -ErrorAction Continue
    exit 1
}
