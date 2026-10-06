@echo off
setlocal
cd /d "%~dp0\..\.."
if "%~1"=="" goto usage
python ops\hermes\hermes-health.py %*
exit /b %ERRORLEVEL%
:usage
echo Hermes health utility
echo   hermes-health.bat status
echo   hermes-health.bat heartbeat --head bharath --seq 1
echo   hermes-health.bat heartbeat --head laxman --seq 1
echo   hermes-health.bat evaluate --head bharath --timeout 90
exit /b 2
