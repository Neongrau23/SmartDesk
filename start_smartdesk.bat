@echo off
:: SmartDesk Starter
:: Nutzt pythonw.exe, um die Konsole im Hintergrund zu halten.

setlocal
cd /d "%~dp0"

:: Prüfe ob Virtual Environment existiert
if not exist ".venv\Scripts\pythonw.exe" (
    echo [FEHLER] Virtual Environment nicht gefunden.
    echo Bitte fuehren Sie zuerst 'scripts\install.bat' aus, um das Programm einzurichten.
    echo.
    pause
    exit /b 1
)

:: Starte SmartDesk Tray-Icon im Hintergrund
start "" ".venv\Scripts\pythonw.exe" "main.py" start-tray

exit
