# ----------------------------------------------------------------------
#  PowerShell-Startskript für SmartDesk (aus dem 'scripts'-Ordner)
# ----------------------------------------------------------------------

# Bricht das Skript ab, wenn ein Befehl fehlschlägt
$ErrorActionPreference = "Stop"

# --- 1. Pfad-Setup ---
# Holt den Pfad, in dem dieses Skript selbst liegt (z.B. .../Projekt/scripts)
$ScriptDir = Split-Path -Path $MyInvocation.MyCommand.Path -Parent
Set-Location $ScriptDir
Write-Host "Aktueller Ordner (Skript-Ordner): $ScriptDir"

# --- 2. Backup-Skript ausführen ---
Write-Host "--- Führe Backup-Skript aus (im selben Ordner) ---"
# Da backup_reg_paths.py im selben Ordner liegt, können wir es direkt aufrufen
python backup_reg_paths.py
Write-Host "Backup abgeschlossen."

# --- 3. Ins Hauptverzeichnis wechseln ---
Write-Host "--- Wechsle ins Hauptverzeichnis ---"
Set-Location ".."
$ProjectDir = Get-Location
Write-Host "Arbeitsverzeichnis ist jetzt: $ProjectDir"

# --- 4. Virtual Environment erstellen (falls nicht vorhanden) ---
# (Pfade sind jetzt relativ zum Hauptverzeichnis)
if (-not (Test-Path -Path ".venv")) {
    Write-Host "--- .venv nicht gefunden. Erstelle Virtual Environment... ---"
    python -m venv .venv
} else {
    Write-Host "--- .venv bereits vorhanden. ---"
}

# --- 5. Anforderungen installieren (mit venv-Python) ---
Write-Host "--- Installiere Anforderungen und aktualisiere Pip ---"
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install --upgrade pip

# --- 6. Hauptanwendung starten (mit venv-Python) ---
Write-Host "--- Starte SmartDesk Tray-Anwendung (als separaten Prozess) ---"
# Start-Process nutzt den Pfad, den wir in Schritt 3 gesetzt haben
Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "src/smartdesk/main.py start-tray"

# --- 7. Beenden ---
Write-Host "--- Skript wird beendet. ---"
exit