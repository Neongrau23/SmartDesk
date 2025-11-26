@echo off
TITLE Registry-Pfade wiederherstellen

REM Stellt sicher, dass die .bat-Datei im selben Verzeichnis wie das Python-Skript ausgeführt wird.
cd /d "%~dp0"

echo Starte Python-Skript zur Wiederherstellung der Registry-Pfade...
echo.

REM Führt das Python-Skript aus. 
REM Dies setzt voraus, dass 'python' in Ihrer System-PATH-Variable registriert ist.
python restore_reg_paths.py

echo.
echo Das Skript wurde beendet.
REM Hält das Fenster offen, damit Sie die Ausgabe lesen können.
pause