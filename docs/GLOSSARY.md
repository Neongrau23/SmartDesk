# Glossar für SmartDesk

Dieses Glossar definiert wichtige Begriffe und Abkürzungen, die im Kontext von SmartDesk und seiner Dokumentation verwendet werden.

---

### Active Desktop (Aktiver Desktop)

Der virtuelle Desktop, der momentan für den Benutzer sichtbar ist. Technisch gesehen ist dies der Desktop, dessen **Desktop Path** aktuell in der Windows-Registrierung eingetragen ist.

### Auto-Switch

Eine Funktion von SmartDesk, die den aktiven Desktop automatisch wechselt, wenn eine vom Benutzer definierte Anwendung (Prozess) gestartet wird.

### Control Panel (Bedienfeld)

Die grafische Benutzeroberfläche (GUI) von SmartDesk. Im Control Panel können Benutzer neue Desktops erstellen, bestehende verwalten, Einstellungen ändern und Regeln für den Auto-Switch festlegen.

### Desktop Configuration (Desktop-Konfiguration)

Die Gesamtheit der Einstellungen, die einen virtuellen Desktop definieren. Dazu gehören der Name, der **Desktop Path**, die gespeicherten **Icon Positions** und der Pfad zum zugewiesenen Hintergrundbild.

### Desktop Path (Desktop-Pfad)

Der Pfad zu einem Ordner im Dateisystem (z.B. `C:\Users\IhrName\Desktop-Arbeit`), dessen Inhalt als Desktop-Symbole angezeigt wird, wenn der zugehörige virtuelle Desktop aktiv ist.

### Explorer Restart (Explorer-Neustart)

Der Vorgang, bei dem der Windows-Prozess `explorer.exe` beendet und neu gestartet wird. Dies ist ein notwendiger Schritt, damit Änderungen am **Desktop Path** in der Windows-Registrierung wirksam werden.

### Hotkey

Eine globale Tastenkombination, die eine SmartDesk-Aktion auslöst (z.B. das Öffnen des Control Panels oder das Wechseln zu einem bestimmten Desktop), unabhängig davon, welche Anwendung gerade im Vordergrund ist.

### Icon Position

Eine Datenstruktur, die den Namen eines Desktop-Symbols sowie seine exakten X- und Y-Koordinaten auf dem Bildschirm speichert. SmartDesk verwendet Listen dieser Objekte, um Desktop-Layouts zu sichern und wiederherzustellen.

### Protected Desktop (Geschützter Desktop)

Ein als "geschützt" markierter Desktop (standardmäßig der "Original"-Desktop), der nicht über die Benutzeroberfläche gelöscht oder bearbeitet werden kann. Dies dient als Sicherheitsmaßnahme, um sicherzustellen, dass der Benutzer immer einen funktionierenden Fallback-Desktop hat.

### Rule (Regel für Auto-Switch)

Eine vom Benutzer erstellte Verknüpfung zwischen einem Prozessnamen (z.B. `Photoshop.exe`) und dem Namen eines virtuellen Desktops. Wenn der Prozess läuft, wird der verknüpfte Desktop durch die **Auto-Switch**-Funktion aktiviert.

### System Tray

Der Benachrichtigungsbereich der Windows-Taskleiste, üblicherweise unten rechts neben der Uhr. Das SmartDesk-Icon befindet sich hier und bietet schnellen Zugriff auf das Hauptmenü der Anwendung.

### Virtual Desktop (Virtueller Desktop)

Das Kernkonzept von SmartDesk. Es handelt sich hierbei nicht um eine separate Windows-Instanz (wie bei der "Task-Ansicht"), sondern um einen benutzerdefinierten Arbeitsbereich. SmartDesk verwaltet den *Inhalt* des primären Windows-Desktops, indem es dessen zugrunde liegenden Ordnerpfad ändert und das Layout der Icons sowie das Hintergrundbild anpasst.

### Windows Registry

Eine zentrale, hierarchische Datenbank in Windows, die Konfigurationseinstellungen für das Betriebssystem und installierte Anwendungen speichert. SmartDesk modifiziert spezifische Schlüssel in der Registry (`HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders`), um den **Desktop Path** zu ändern.
