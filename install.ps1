[CmdletBinding()]
param(
    [string]$PythonPath,
    [string]$PnpmPath,
    [string]$NodePath,
    [switch]$VerifySourceOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$rootPath = [IO.Path]::GetFullPath($PSScriptRoot)
$sourcePath = Join-Path $rootPath 'agentscope'
$upstreamCommit = '58da57a565832ac3710d0f22318a5d0ee326a406'
$upstreamUrl = 'https://github.com/agentscope-ai/agentscope.git'
$bundledRoot = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.cache\codex-runtimes\codex-primary-runtime\dependencies'
$taskCachePath = Join-Path $rootPath '.cache'

function Invoke-Checked([string]$Executable, [string[]]$Arguments) {
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed (exit $LASTEXITCODE): $Executable $($Arguments -join ' ')"
    }
}

function Get-CandidatePaths([string]$Explicit, [string]$CommandName, [string[]]$Fallbacks) {
    if ($Explicit) {
        if (-not (Test-Path -LiteralPath $Explicit -PathType Leaf)) {
            throw "Requested executable does not exist: $Explicit"
        }
        return @([IO.Path]::GetFullPath($Explicit))
    }
    $paths = @()
    $commands = @(Get-Command $CommandName -All -CommandType Application -ErrorAction SilentlyContinue)
    foreach ($command in $commands) { $paths += $command.Source }
    $paths += $Fallbacks
    return @($paths | Where-Object {
        $_ -and $_ -notmatch '[\\/]Microsoft[\\/]WindowsApps[\\/]' -and (Test-Path -LiteralPath $_ -PathType Leaf)
    } | Select-Object -Unique)
}

function Test-SourceManifest {
    $manifestPath = Join-Path $rootPath 'UPSTREAM.json'
    if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        throw 'Source without .git requires UPSTREAM.json from the complete source package. Nothing was replaced.'
    }
    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($manifest.schema_version -ne 1 -or $manifest.project -ne 'agent-control-console' -or
        $manifest.upstream.commit -ne $upstreamCommit -or $manifest.upstream.repository -ne $upstreamUrl) {
        throw 'UPSTREAM.json does not match the pinned project and official upstream commit.'
    }
    $requiredPaths = @(
        'agentscope/LICENSE', 'agentscope/pyproject.toml',
        'agentscope/src/agentscope/_version.py', 'agentscope/src/agentscope/app/_app.py',
        'agentscope/examples/web_ui/frontend/package.json',
        'agentscope/examples/web_ui/frontend/src/App.tsx',
        'agentscope/examples/web_ui/frontend/src/api/vault.ts',
        'agentscope/examples/web_ui/frontend/src/pages/vault/index.tsx',
        'agentscope/examples/web_ui/frontend/dist/index.html',
        'control/main.py', 'control/vault.py', 'control/requirements.txt', 'control/requirements.lock.txt'
    )
    $verifiedPaths = @{}
    $checkedCount = 0
    foreach ($entry in @($manifest.files)) {
        if (-not $entry.verify_on_install) { continue }
        $relative = [string]$entry.path
        if (-not $relative -or $relative.Contains('\') -or [IO.Path]::IsPathRooted($relative) -or
            $relative -match '(^|/)(\.\.?|)(/|$)' -or $relative.Contains(':') -or
            [string]$entry.sha256 -notmatch '^[a-fA-F0-9]{64}$' -or $verifiedPaths.ContainsKey($relative)) {
            throw "Invalid or duplicate path/hash in UPSTREAM.json: $relative"
        }
        $targetPath = [IO.Path]::GetFullPath((Join-Path $rootPath $relative.Replace('/', '\')))
        if (-not $targetPath.StartsWith($rootPath + '\', [StringComparison]::OrdinalIgnoreCase)) {
            throw "Manifest path escaped the project root: $relative"
        }
        $cursorPath = $rootPath
        foreach ($segment in $relative.Split('/')) {
            $cursorPath = Join-Path $cursorPath $segment
            $item = Get-Item -LiteralPath $cursorPath -Force -ErrorAction Stop
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "Manifest files must not traverse a symbolic link or junction: $relative"
            }
        }
        if (-not (Test-Path -LiteralPath $targetPath -PathType Leaf) -or
            (Get-FileHash -LiteralPath $targetPath -Algorithm SHA256).Hash -ne [string]$entry.sha256) {
            throw "Packaged source checksum differs: $relative. Existing files were preserved; restore or repackage your reviewed changes."
        }
        $verifiedPaths[$relative] = $true
        $checkedCount++
    }
    foreach ($requiredPath in $requiredPaths) {
        if (-not $verifiedPaths.ContainsKey($requiredPath)) {
            throw "UPSTREAM.json is missing a required verified source: $requiredPath"
        }
    }
    Write-Host "Verified $checkedCount packaged source files against UPSTREAM.json."
}

try {
    $taskTempPath = Join-Path $taskCachePath 'tmp'
    $pipCachePath = Join-Path $taskCachePath 'pip'
    $pnpmStorePath = Join-Path $taskCachePath 'pnpm-store'
    New-Item -ItemType Directory -Path $taskTempPath, $pipCachePath, $pnpmStorePath -Force | Out-Null
    $env:TEMP = $taskTempPath
    $env:TMP = $taskTempPath
    $env:PIP_CACHE_DIR = $pipCachePath
    $env:PYTHONUTF8 = '1'
    $env:PYTHONIOENCODING = 'utf-8'
    # Installing this application must not install Git hooks into upstream.
    $env:HUSKY = '0'
    if (-not (Test-Path -LiteralPath $sourcePath)) {
        throw 'agentscope is missing. Restore the complete source package, including the customized frontend. Nothing will be downloaded or replaced automatically.'
    }
    if (Test-Path -LiteralPath (Join-Path $sourcePath '.git')) {
        $gitCommand = Get-Command git.exe -CommandType Application -ErrorAction Stop
        $currentCommit = (& $gitCommand.Source -C $sourcePath rev-parse HEAD).Trim()
        if ($LASTEXITCODE -ne 0) { throw 'Cannot inspect the existing AgentScope checkout.' }
        if ($currentCommit -ne $upstreamCommit) {
            throw "AgentScope is at $currentCommit; expected $upstreamCommit. Existing files were preserved."
        }
        $remoteUrl = (& $gitCommand.Source -C $sourcePath remote get-url origin).Trim()
        if ($LASTEXITCODE -ne 0 -or $remoteUrl -notmatch '^(https://github\.com/agentscope-ai/agentscope(?:\.git)?/?|git@github\.com:agentscope-ai/agentscope(?:\.git)?|ssh://git@github\.com/agentscope-ai/agentscope(?:\.git)?)$') {
            throw 'The existing AgentScope origin is not the expected official repository. It was preserved.'
        }
        Write-Host "Verified upstream commit $upstreamCommit. Local changes will be kept."
    } else {
        Test-SourceManifest
    }
    if ($VerifySourceOnly) {
        Write-Host 'Source verification complete. No dependencies were downloaded and no service was started.'
        exit 0
    }

    $requirementsPath = Join-Path $rootPath 'control\requirements.txt'
    if (-not (Test-Path -LiteralPath $requirementsPath -PathType Leaf)) {
        throw 'control/requirements.txt is missing. Restore the full project first.'
    }
    $constraintsPath = Join-Path $rootPath 'control\requirements.lock.txt'
    if (-not (Test-Path -LiteralPath $constraintsPath -PathType Leaf)) {
        throw 'control/requirements.lock.txt is missing. Restore the full project first.'
    }
    $venvPath = Join-Path $rootPath '.venv'
    $venvPython = Join-Path $venvPath 'Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
        if (Test-Path -LiteralPath $venvPath) {
            throw '.venv already exists without Scripts/python.exe. It has not been overwritten.'
        }
        $basePython = $null
        $pythonCandidates = @(Get-CandidatePaths $PythonPath 'python.exe' @(
            (Join-Path $bundledRoot 'python\python.exe')
        ))
        foreach ($candidate in $pythonCandidates) {
            if ($candidate -match '[\\/]Microsoft[\\/]WindowsApps[\\/]') { continue }
            $probe = & $candidate -c 'import sys; print(sys.executable); raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' 2>$null
            if ($LASTEXITCODE -eq 0 -and $probe) { $basePython = $candidate; break }
        }
        if (-not $basePython) { throw 'Python 3.11+ was not found. Install it or pass -PythonPath C:\path\python.exe.' }
        Invoke-Checked $basePython @('-m', 'venv', $venvPath)
    }
    Invoke-Checked $venvPython @('-c', 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)')

    $nodeExecutable = $null
    $nodeCandidates = @(Get-CandidatePaths $NodePath 'node.exe' @(
        (Join-Path $bundledRoot 'node\bin\node.exe'),
        (Join-Path $bundledRoot 'bin\node.exe')
    ))
    foreach ($candidate in $nodeCandidates) {
        & $candidate -e 'const [a,b] = process.versions.node.split(String.fromCharCode(46)).map(Number); process.exit((a === 20 && b >= 19) || (a === 22 && b >= 12) || a > 22 ? 0 : 1)' 2>$null
        if ($LASTEXITCODE -eq 0) { $nodeExecutable = $candidate; break }
    }
    if (-not $nodeExecutable) { throw 'Node.js 20.19+ or 22.12+ was not found. Install Node.js 22+ or pass -NodePath.' }
    $env:PATH = "$(Split-Path -Parent $nodeExecutable);$env:PATH"
    $pnpmCandidates = @(Get-CandidatePaths $PnpmPath 'pnpm.cmd' @(
        (Join-Path $bundledRoot 'bin\fallback\pnpm.cmd')
    ))
    if ($pnpmCandidates.Count -eq 0) {
        throw 'pnpm was not found. Install pnpm 10 or pass -PnpmPath C:\path\pnpm.cmd.'
    }
    $pnpmExecutable = $pnpmCandidates[0]
    Invoke-Checked $pnpmExecutable @('--version')

    Push-Location -LiteralPath $rootPath
    try {
        Write-Host 'Installing the local Python service...'
        Invoke-Checked $venvPython @('-m', 'pip', 'install', '--requirement', $requirementsPath, '--constraint', $constraintsPath)
    } finally { Pop-Location }

    $webUiPath = Join-Path $sourcePath 'examples\web_ui'
    Push-Location -LiteralPath $webUiPath
    try {
        Write-Host 'Installing the locked frontend dependencies...'
        Invoke-Checked $pnpmExecutable @('install', '--frozen-lockfile', '--store-dir', $pnpmStorePath)
        Invoke-Checked $pnpmExecutable @('--filter', 'frontend', 'build')
    } finally { Pop-Location }
    if (-not (Test-Path -LiteralPath (Join-Path $webUiPath 'frontend\dist\index.html') -PathType Leaf)) {
        throw 'The frontend build produced no index.html.'
    }
    Write-Host 'Installation complete. Run start.ps1 or double-click the launcher.'
    Write-Host 'No API key was added and no model inference was executed.'
} catch {
    Write-Error $_ -ErrorAction Continue
    exit 1
}
