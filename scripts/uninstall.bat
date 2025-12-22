@echo off
chcp 65001 >nul
title SmartDesk - Deinstallation

echo.
echo ============================================================
echo   SmartDesk - Deinstallation
echo ============================================================
echo.

:: Prüfe ob Python verfügbar ist
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python wurde nicht gefunden!
    echo    Bitte installieren Sie Python oder führen Sie
    echo    das Skript manuell aus.
    echo.
    pause
    exit /b 1
)

:: Zum Skript-Verzeichnis wechseln
cd /d "%~dp0"

:: Virtual Environment aktivieren falls vorhanden
if exist "..\venv\Scripts\activate.bat" (
    call "..\venv\Scripts\activate.bat"
) else if exist "..\.venv\Scripts\activate.bat" (
    call "..\.venv\Scripts\activate.bat"
)

:: Uninstall-Skript ausführen
python uninstall.py

echo.
pause
