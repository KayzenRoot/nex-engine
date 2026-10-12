# NEX Engine native Godot launcher. No download, install, admin or network calls.
[CmdletBinding()]
param(
    [string]$GodotPath = "",
    [switch]$SmokeOnly
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$projectDir = Split-Path -Parent $PSCommandPath
$repoRoot = Split-Path -Parent $projectDir
$toolchain = Join-Path $repoRoot ".nex/toolchain/NEX-M00-WO-001-toolchain-lock.json"

function Stop-Nex([string]$reason) {
    [Console]::Error.WriteLine("NEX_LAUNCH_BLOCKED: " + $reason)
    exit 1
}

try {
    if (-not (Test-Path -LiteralPath $toolchain -PathType Leaf)) {
        Stop-Nex "Pinned M00 toolchain lock is missing."
    }
    $lock = Get-Content -LiteralPath $toolchain -Raw -Encoding UTF8 | ConvertFrom-Json
    $expected = [string]$lock.godot.tag
    if ([string]::IsNullOrWhiteSpace($expected)) {
        Stop-Nex "Missing Godot version in toolchain lock."
    }
    if ([string]::IsNullOrWhiteSpace($GodotPath)) {
        $GodotPath = [string]$env:NEX_GODOT_BIN
    }
    if ([string]::IsNullOrWhiteSpace($GodotPath)) {
        foreach ($name in @("godot.exe", "godot", "godot4.exe", "godot4")) {
            $found = Get-Command -Name $name -CommandType Application -ErrorAction SilentlyContinue |
                Select-Object -First 1
            if ($null -ne $found) {
                $GodotPath = [string]$found.Source
                break
            }
        }
    }
    if ([string]::IsNullOrWhiteSpace($GodotPath)) {
        Stop-Nex "Godot not found. Supply -GodotPath 'C:\path\Godot.exe' or set NEX_GODOT_BIN."
    }
    $candidate = Get-Command -Name $GodotPath -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($null -eq $candidate) {
        Stop-Nex "The selected Godot executable was not found."
    }
    $godot = [string]$candidate.Source
    $versionOutput = (& $godot --version 2>&1 | Out-String).Trim()
    $versionExit = $LASTEXITCODE
    if ($versionExit -ne 0) {
        Stop-Nex "Could not read Godot version (exit $versionExit)."
    }
    $expectedVersion = $expected.Replace("-stable", ".stable")
    if (-not $versionOutput.StartsWith($expectedVersion, [System.StringComparison]::OrdinalIgnoreCase)) {
        Stop-Nex "Godot $expected required by M00; found '$versionOutput'."
    }
    Write-Host "NEX: verified Godot $versionOutput"
    Write-Host "NEX: checking 4 modules with local headless smoke..."
    $smokeOutput = (& $godot --headless --path $projectDir --rendering-method gl_compatibility --script "res://smoke.gd" 2>&1 | Out-String)
    $smokeExit = $LASTEXITCODE
    Write-Host $smokeOutput
    if ($smokeExit -ne 0 -or -not $smokeOutput.Contains("NEX_NATIVE_IMPORT_SMOKE_PASS")) {
        Stop-Nex "Native Godot smoke failed (exit $smokeExit). Do not launch GUI until fixed."
    }
    Write-Host "NEX_NATIVE_STARTUP_VALIDATED: smoke passed."
    if ($SmokeOnly) {
        exit 0
    }
    # Start-Process avoids invoking arbitrary shell source, and keeps GUI asynchronous.
    $projectArgument = '--path "' + $projectDir.Replace('"', '') + '"'
    $process = Start-Process -FilePath $godot -ArgumentList $projectArgument -WorkingDirectory $projectDir -PassThru
    Write-Host "NEX_GUI_STARTED: pid=$($process.Id); F1-F4 scenes, B/N screenshots, D compare."
    exit 0
}
catch {
    Stop-Nex ([string]$_)
}
