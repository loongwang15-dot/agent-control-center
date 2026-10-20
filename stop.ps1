[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$rootPath = [IO.Path]::GetFullPath($PSScriptRoot)
$pythonPath = Join-Path $rootPath '.venv\Scripts\python.exe'
$recordPath = Join-Path $rootPath 'runtime\server.json'
$statusUrl = 'http://127.0.0.1:8765/control/status'

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

try {
    if (-not (Test-Path -LiteralPath $recordPath -PathType Leaf)) {
        Write-Host 'No owned service record exists. No process has been stopped.'
        exit 0
    }
    $record = Get-Content -LiteralPath $recordPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($record.project -ne 'agent-control-console' -or
        -not [string]::Equals([string]$record.root, $rootPath, [StringComparison]::OrdinalIgnoreCase) -or
        -not [string]::Equals([string]$record.python_path, $pythonPath, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'The service record does not belong to this project. No process has been stopped.'
    }
    $serverProcessId = 0
    if (-not [int]::TryParse([string]$record.pid, [ref]$serverProcessId) -or $serverProcessId -le 0) {
        throw 'The service record has no valid process ID.'
    }
    $serverProcess = Get-Process -Id $serverProcessId -ErrorAction SilentlyContinue
    if ($null -eq $serverProcess) {
        Remove-Item -LiteralPath $recordPath
        Write-Host 'The recorded process has already exited.'
        exit 0
    }
    $recordStart = [DateTime]::Parse([string]$record.process_start_utc).ToUniversalTime()
    if ([Math]::Abs(($serverProcess.StartTime.ToUniversalTime() - $recordStart).TotalSeconds) -gt 1) {
        throw 'The process ID has been reused. No process has been stopped.'
    }
    try {
        $response = Invoke-WebRequest -Uri $statusUrl -TimeoutSec 3 -Method Get -UseBasicParsing
        if ($response.RawContentStream.CanSeek) { $response.RawContentStream.Position = 0 }
        $reader = [IO.StreamReader]::new($response.RawContentStream, [Text.Encoding]::UTF8)
        try { $health = $reader.ReadToEnd() | ConvertFrom-Json }
        finally { $reader.Dispose() }
    } catch {
        throw 'Cannot verify the live project health response. Refusing to stop any process; inspect runtime logs.'
    }
    if ($health.project -ne 'agent-control-console' -or [int]$health.pid -ne $serverProcessId -or
        -not (Test-SamePath ([string]$health.root) $rootPath) -or
        -not (Test-SamePath ([string]$health.python_executable) $pythonPath)) {
        throw 'The live service and the ownership record do not match. No process has been stopped.'
    }
    $expectedBasePython = Get-ExpectedBasePython
    $directVenvProcess = Test-SamePath $serverProcess.Path $pythonPath
    $verifiedBaseProcess = (Test-SamePath $serverProcess.Path $expectedBasePython) -and
        (Test-SamePath ([string]$health.python_base_executable) $expectedBasePython)
    if ((-not $directVenvProcess -and -not $verifiedBaseProcess) -or
        -not (Test-SamePath $serverProcess.Path ([string]$record.process_path)) -or
        -not (Test-SamePath $expectedBasePython ([string]$record.python_base_path))) {
        throw 'The executable path or base Python no longer matches the verified record. No process has been stopped.'
    }
    # The project, PID, executable and process creation time have all matched.
    Stop-Process -Id $serverProcessId -ErrorAction Stop
    $serverProcess.WaitForExit(10000) | Out-Null
    $serverProcess.Refresh()
    if (-not $serverProcess.HasExited) {
        throw 'The process did not exit. The ownership record was preserved.'
    }
    Remove-Item -LiteralPath $recordPath
    Write-Host "Stopped project service (PID $serverProcessId). Data and logs have been retained."
} catch {
    Write-Error $_ -ErrorAction Continue
    exit 1
}
