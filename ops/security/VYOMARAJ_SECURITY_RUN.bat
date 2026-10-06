@echo off
setlocal
cd /d "%~dp0..\.."
where powershell.exe >nul 2>&1 || (echo PowerShell is required.&exit /b 10)
echo VYOMARAJ SECURITY GUARD
echo 1 Audit  2 Baseline  3 Incident  4 Verify
set /p MODE="Select: "
if "%MODE%"=="2" set RUNMODE=Baseline
if "%MODE%"=="3" set RUNMODE=Incident
if "%MODE%"=="4" set RUNMODE=Verify
if not defined RUNMODE set RUNMODE=Audit
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "ops\security\VYOMARAJ_SECURITY_CORE.ps1" -Mode "%RUNMODE%"
set RC=%ERRORLEVEL%
echo Report: reports\security\latest-security-report.json
if %RC%==0 echo STATUS: PASS
if %RC%==1 echo STATUS: REVIEW REQUIRED
if %RC%==2 echo STATUS: CRITICAL - CONTAIN AND INVESTIGATE
exit /b %RC%