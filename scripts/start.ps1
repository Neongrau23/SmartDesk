# ----------------------------------------------------------------------
#  PowerShell-Startskript für SmartDesk
# ----------------------------------------------------------------------

# Bricht das Skript ab, wenn ein Befehl fehlschlägt
$ErrorActionPreference = "Stop"

# Holt den Pfad, in dem dieses Skript selbst liegt
# (damit es egal ist, von wo aus Sie es starten)
$ScriptDir = Split-Path -Path $MyInvocation.MyCommand.Path -Parent
Set-Location $ScriptDir

Write-Host "Arbeitsverzeichnis: $ScriptDir"

# --- 1. Backup-Skript ausführen ---
Write-Host "--- Führe Backup-Skript aus ---"
Set-Location "scripts"
python backup_reg_paths.py
Set-Location ".."
Write-Host "Backup abgeschlossen."

# --- 2. Virtual Environment erstellen (falls nicht vorhanden) ---
if (-not (Test-Path -Path ".venv")) {
    Write-Host "--- .venv nicht gefunden. Erstelle Virtual Environment... ---"
    python -m venv .venv
} else {
    Write-Host "--- .venv bereits vorhanden. ---"
}

# --- 3. Anforderungen installieren (mit venv-Python) ---
Write-Host "--- Installiere Anforderungen und aktualisiere Pip ---"
# 
# HINWEIS: Wir rufen Python/Pip direkt aus dem venv-Ordner auf.
# Dies ist zuverlässiger als der Versuch, '.venv\Scripts\Activate.ps1'
# auszuführen, was oft an der Execution Policy scheitert.
#
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install --upgrade pip

# --- 4. Hauptanwendung starten (mit venv-Python) ---
Write-Host "--- Starte SmartDesk Tray-Anwendung ---"
.\.venv\Scripts\python.exe src/smartdesk/main.py start-tray

# --- 5. Beenden ---
exit