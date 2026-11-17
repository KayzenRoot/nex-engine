param(
    [string]$Exe = "",
    [string]$Output = ""
)
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
if ([string]::IsNullOrWhiteSpace($Exe)) { $Exe = Join-Path $repo "build\NEXEngine.exe" }
if ([string]::IsNullOrWhiteSpace($Output)) { $Output = Join-Path $repo "docs\benchmarks\build\evidence" }
if (-not (Test-Path -LiteralPath $Exe -PathType Leaf)) { Write-Output "NEX_GUI_BLOCKED: executable missing: $Exe"; exit 2 }
New-Item -ItemType Directory -Force -Path $Output | Out-Null

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class NexWin32 {
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
}
"@

$process = Start-Process -FilePath $Exe -WorkingDirectory (Split-Path -Parent $Exe) -PassThru
Start-Sleep -Seconds 10
if ($process.HasExited) { Write-Output "NEX_GUI_BLOCKED: exited early with $($process.ExitCode)"; exit 1 }
$shell = New-Object -ComObject WScript.Shell
if (-not $shell.AppActivate($process.Id)) {
    Stop-Process -Id $process.Id -Force
    Write-Output "NEX_GUI_BLOCKED: could not focus the window"
    exit 1
}

function Capture([string]$name) {
    $process.Refresh()
    $handle = $process.MainWindowHandle
    if ($handle -eq [IntPtr]::Zero) { throw "window handle unavailable" }
    $rect = New-Object NexWin32+RECT
    if (-not [NexWin32]::GetWindowRect($handle, [ref]$rect)) { throw "GetWindowRect failed" }
    $width = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top
    if ($width -lt 640 -or $height -lt 360) { throw "window too small: ${width}x${height}" }
    $bitmap = New-Object System.Drawing.Bitmap $width, $height
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.CopyFromScreen($rect.Left, $rect.Top, 0, 0, $bitmap.Size)
    $path = Join-Path $Output $name
    $bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose()
    $bitmap.Dispose()
    Write-Output "NEX_GUI_CAPTURE: $name ${width}x${height}"
}

Capture "nex-mode-corridor.png"
$shell.SendKeys("{F2}"); Start-Sleep -Seconds 3; Capture "nex-mode-arena.png"
$shell.SendKeys("{F3}"); Start-Sleep -Seconds 3; Capture "nex-mode-dense-city.png"
$shell.SendKeys("{F4}"); Start-Sleep -Seconds 3; Capture "nex-mode-density.png"
$shell.SendKeys("{F5}"); Start-Sleep -Seconds 4; Capture "nex-mode-arpg.png"
$shell.SendKeys("{F9}"); Start-Sleep -Seconds 2; Capture "nex-mode-diagnostics.png"
Write-Output "NEX_GUI_TESTED: pid=$($process.Id)"
Stop-Process -Id $process.Id -Force
Write-Output "NEX_GUI_STOPPED"
