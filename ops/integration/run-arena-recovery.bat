@echo off
setlocal
title Vyomaraj Jarvis Arena Recovery
where python >nul 2>&1 || (echo Python 3 required.& exit /b 1)
if not defined RECOVERY_OUT_DIR set "RECOVERY_OUT_DIR=.arena-recovery"
REM Optional: set "ARENA_EXPORT_DIRS=C:\Arena\exports;C:\Arena\sessions"
python "%~dp0vyomaraj-jarvis-arena-recovery.py" %*
if errorlevel 1 exit /b 1
echo Recovery complete.
echo Review .arena-recovery\reports\RECOVERY_MANIFEST.json
echo Review .arena-recovery\reports\VYOMARAJ_JARVIS_ARENA_HANDOFF.md
echo Missing Arena backend sessions remain UNRECOVERED until Arena exports them.
