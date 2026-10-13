@echo off
setlocal
REM Run from Explorer to verify pinned Godot, smoke all 4 modules, and open NEX GUI.
REM Optional: Start-NEX.cmd -GodotPath "C:\Tools\Godot.exe"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy RemoteSigned -File "%~dp0Start-NEX.ps1" %*
set "NEX_EXIT=%ERRORLEVEL%"
if not "%NEX_EXIT%"=="0" (
  echo NEX failed. Check the printed version or native smoke error above.
  if not defined CI pause
)
exit /b %NEX_EXIT%
