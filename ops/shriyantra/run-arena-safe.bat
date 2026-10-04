@echo off
setlocal EnableExtensions
REM Safe launcher for ShriYantra/Arena. It never prints approval tokens or secrets.
cd /d "%~dp0\..\.."
if errorlevel 1 (
  echo [DENIED] Could not enter repository root.
  exit /b 2
)
if "%~1"=="" goto usage
if /I "%~1"=="init" (
  python ops\shriyantra\shriyantra-arena.py init
  exit /b %ERRORLEVEL%
)
if /I "%~1"=="health" (
  python ops\shriyantra\shriyantra-arena.py health
  exit /b %ERRORLEVEL%
)
if /I "%~1"=="task" (
  shift
  python ops\shriyantra\shriyantra-arena.py task %*
  exit /b %ERRORLEVEL%
)
:usage
echo Usage:
echo   ops\shriyantra\run-arena-safe.bat init
echo   ops\shriyantra\run-arena-safe.bat health
echo   ops\shriyantra\run-arena-safe.bat task --task "Audit repository" --head BHARATH
echo   Add --execute only after the trusted ShriYantra approval service and reviewed Arena adapter are configured.
exit /b 2
