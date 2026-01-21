@echo off
chcp 65001 >nul
title SmartDesk - Installation

echo.
echo ============================================================
echo   SmartDesk - Installation und Einrichtung
echo ============================================================
echo.

:: Prüfe ob Python verfügbar ist
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python wurde nicht gefunden!
    echo.
    echo    Bitte installieren Sie Python 3.8 oder höher:
    echo    https://www.python.org/downloads/
    echo.
    echo    Stellen Sie sicher, dass "Add Python to PATH"
    echo    bei der Installation aktiviert ist.
    echo.
    pause
    exit /b 1
)

:: Zum Skript-Verzeichnis wechseln
cd /d "%~dp0"
cd ..

:: Install-Skript ausführen
python scripts\install.py %*

if errorlevel 1 (
    echo.
    echo ❌ Installation fehlgeschlagen!
    echo.
    pause
    exit /b 1
)
