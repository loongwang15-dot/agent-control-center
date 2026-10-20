@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0stop.ps1" %*
if errorlevel 1 (
  echo.
  echo Stop was refused or failed. No unverified process will be terminated.
  pause
  exit /b 1
)
exit /b 0
