@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1" %*
if errorlevel 1 (
  echo.
  echo Startup failed. Read the message above and runtime\server.stderr.log.
  pause
  exit /b 1
)
exit /b 0
