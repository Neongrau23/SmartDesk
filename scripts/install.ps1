#Requires -Version 5.1
<#
.SYNOPSIS
    SmartDesk Installation und Start-Skript

.DESCRIPTION
    Dieses Skript führt eine vollständige Installation durch:
    - Prüft Voraussetzungen (Python, Windows)
    - Erstellt Virtual Environment
    - Installiert Abhängigkeiten
    - Führt First-Run-Setup durch
    - Startet SmartDesk

.PARAMETER NoStart
    Führt nur die Installation durch, ohne SmartDesk zu starten

.PARAMETER Check
    Prüft nur die Voraussetzungen

.EXAMPLE
    .\install.ps1
    Vollständige Installation und Start des Tray-Icons

.EXAMPLE
    .\install.ps1 -NoStart
    Nur Installation, kein automatischer Start
#>

param(
    [switch]$NoStart,
    [switch]$Check
)

$ErrorActionPreference = "Stop"

# Konfiguration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$VenvDir = Join-Path $ProjectRoot ".venv"
$SrcDir = Join-Path $ProjectRoot "src"
$RequirementsFile = Join-Path $ProjectRoot "requirements.txt"

function Write-Header {
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host "  🖥️  SmartDesk - Installation & Einrichtung" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param([int]$Step, [int]$Total, [string]$Message)
    Write-Host ""
    Write-Host "[$Step/$Total] $Message" -ForegroundColor Yellow
    Write-Host ("-" * 50) -ForegroundColor DarkGray
}

function Write-Success {
    param([string]$Message)
    Write-Host "  ✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "  ⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "  ❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "  ℹ️  $Message" -ForegroundColor Cyan
}

# Voraussetzungen prüfen
function Test-Prerequisites {
    # Windows prüfen
    if ($env:OS -ne "Windows_NT") {
        Write-Error "SmartDesk ist nur für Windows verfügbar!"
        return $false
    }
    Write-Success "Windows erkannt"

    # Python prüfen
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            Write-Info "Python-Version: $major.$minor"

            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
                Write-Error "Python 3.8+ erforderlich!"
                return $false
            }
            Write-Success "Python-Version OK"
        }
    }
    catch {
        Write-Error "Python nicht gefunden! Bitte Python 3.8+ installieren."
        return $false
    }

    # requirements.txt prüfen
    if (-not (Test-Path $RequirementsFile)) {
        Write-Error "requirements.txt nicht gefunden!"
        return $false
    }
    Write-Success "requirements.txt gefunden"

    return $true
}

# Virtual Environment erstellen
function New-VirtualEnvironment {
    if (Test-Path $VenvDir) {
        Write-Info "Virtual Environment existiert bereits"
        return $true
    }

    Write-Info "Erstelle Virtual Environment..."
    python -m venv $VenvDir

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Virtual Environment erstellt"
        return $true
    }
    else {
        Write-Error "Fehler beim Erstellen des Virtual Environment"
        return $false
    }
}

# Abhängigkeiten installieren
function Install-Dependencies {
    $pipPath = Join-Path $VenvDir "Scripts\pip.exe"

    if (-not (Test-Path $pipPath)) {
        Write-Error "pip nicht gefunden!"
        return $false
    }

    Write-Info "Aktualisiere pip..."
    & $pipPath install --upgrade pip 2>&1 | Out-Null

    Write-Info "Installiere Abhängigkeiten..."
    & $pipPath install -r $RequirementsFile

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Alle Abhängigkeiten installiert"
        return $true
    }
    else {
        Write-Error "Fehler bei der Installation"
        return $false
    }
}

# First-Run Setup
function Invoke-FirstRunSetup {
    $pythonPath = Join-Path $VenvDir "Scripts\python.exe"
    $mainScript = Join-Path $SrcDir "smartdesk\main.py"

    # Prüfe ob Setup bereits durchgeführt
    $setupFile = Join-Path $env:APPDATA "SmartDesk\setup.json"

    if (Test-Path $setupFile) {
        Write-Info "Setup wurde bereits durchgeführt"

        # Prüfe Original Desktop
        $desktopsFile = Join-Path $env:APPDATA "SmartDesk\desktops.json"
        if (Test-Path $desktopsFile) {
            $desktops = Get-Content $desktopsFile | ConvertFrom-Json
            $hasOriginal = $desktops | Where-Object { $_.protected -eq $true }
            if ($hasOriginal) {
                Write-Success "Original Desktop existiert"
                return $true
            }
        }
    }

    Write-Info "Führe First-Run-Setup durch..."

    Set-Location $ProjectRoot
    $env:PYTHONPATH = $SrcDir

    & $pythonPath -c @"
import sys
sys.path.insert(0, 'src')
from smartdesk.shared.first_run import run_first_time_setup, create_original_desktop
result = run_first_time_setup(silent=False)
create_original_desktop(silent=False)
"@

    Write-Success "First-Run-Setup abgeschlossen"
    return $true
}

# Installation verifizieren
function Test-Installation {
    $pythonPath = Join-Path $VenvDir "Scripts\python.exe"

    Set-Location $ProjectRoot
    & $pythonPath -c @"
import sys
sys.path.insert(0, 'src')
from smartdesk.core.services.desktop_service import get_all_desktops
desktops = get_all_desktops()
print(f'Gefundene Desktops: {len(desktops)}')
for d in desktops:
    status = '🔒' if d.protected else '📁'
    active = ' [AKTIV]' if d.is_active else ''
    print(f'  {status} {d.name}{active}')
"@

    return $LASTEXITCODE -eq 0
}

# SmartDesk starten
function Start-SmartDesk {
    $pythonPath = Join-Path $VenvDir "Scripts\python.exe"
    $mainScript = Join-Path $SrcDir "smartdesk\main.py"

    Set-Location $ProjectRoot

    Write-Info "Starte SmartDesk Tray-Icon..."
    Start-Process -FilePath $pythonPath -ArgumentList $mainScript, "start-tray" -WindowStyle Hidden
    Write-Success "Tray-Icon gestartet"
    Write-Info "SmartDesk läuft jetzt im System Tray (neben der Uhr)"
}

# Hauptlogik
function Main {
    Write-Header

    $totalSteps = if ($Check) { 1 } else { 6 }
    $currentStep = 0

    # Schritt 1: Voraussetzungen
    $currentStep++
    Write-Step -Step $currentStep -Total $totalSteps -Message "Voraussetzungen prüfen"

    if (-not (Test-Prerequisites)) {
        return 1
    }

    if ($Check) {
        Write-Host ""
        Write-Host "✅ Alle Voraussetzungen erfüllt!" -ForegroundColor Green
        return 0
    }

    # Schritt 2: Virtual Environment
    $currentStep++
    Write-Step -Step $currentStep -Total $totalSteps -Message "Virtual Environment einrichten"

    if (-not (New-VirtualEnvironment)) {
        return 1
    }

    # Schritt 3: Abhängigkeiten
    $currentStep++
    Write-Step -Step $currentStep -Total $totalSteps -Message "Abhängigkeiten installieren"

    if (-not (Install-Dependencies)) {
        return 1
    }

    # Schritt 4: First-Run Setup
    $currentStep++
    Write-Step -Step $currentStep -Total $totalSteps -Message "SmartDesk einrichten"

    Invoke-FirstRunSetup | Out-Null

    # Schritt 5: Verifizierung
    $currentStep++
    Write-Step -Step $currentStep -Total $totalSteps -Message "Installation überprüfen"

    if (Test-Installation) {
        Write-Success "Installation erfolgreich!"
    }
    else {
        Write-Warning "Verifikation fehlgeschlagen (nicht kritisch)"
    }

    # Schritt 6: Start
    $currentStep++
    Write-Step -Step $currentStep -Total $totalSteps -Message "SmartDesk starten"

    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Green
    Write-Host "  ✅ Installation abgeschlossen!" -ForegroundColor Green
    Write-Host "=" * 60 -ForegroundColor Green
    Write-Host ""

    if ($NoStart) {
        Write-Info "Start übersprungen (-NoStart)"
        Write-Host ""
        Write-Host "  Starten Sie SmartDesk mit:" -ForegroundColor Cyan
        Write-Host "    .\scripts\install.ps1" -ForegroundColor White
        Write-Host "  oder:" -ForegroundColor Cyan
        Write-Host "    python src\smartdesk\main.py" -ForegroundColor White
        return 0
    }

    Start-SmartDesk

    Write-Host ""
    Read-Host "Drücken Sie Enter zum Beenden"

    return 0
}

# Ausführen
try {
    Set-Location $ProjectRoot
    exit (Main)
}
catch {
    Write-Host ""
    Write-Host "❌ Fehler: $_" -ForegroundColor Red
    exit 1
}
