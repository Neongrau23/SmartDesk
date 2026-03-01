# ADR 007: Rückkehr zum nativen Betriebssystem-Styling

* **Status:** Akzeptiert
* **Datum:** 2026-03-01
* **Beteiligte:** Leon (Neongrau23), AI-Assistent
* **Tags:** #ui #design #pyside6 #qt #styling

## Kontext

Die grafische Benutzeroberfläche (GUI) von SmartDesk wurde ursprünglich mit einem stark angepassten "Modern Dark Theme" versehen, das von VS Code inspiriert war. Dieses Styling wurde über eine zentrale `style.qss`-Datei in PySide6 injiziert und nutzte Flags wie `Qt.WA_TranslucentBackground`, um komplett eigene Fensterformen und abgerundete Ecken unabhängig vom Betriebssystem (Windows) zu erzwingen.

Obwohl das Design ästhetisch ansprechend war, führte die aggressive Entkopplung vom Betriebssystem-Standard zu Komplikationen bei der Wartbarkeit und der Interaktion mit systemeigenen Fenster-Verhaltensweisen (z.B. Transparenz-Bugs beim Entfernen von Styles).

## Alternativen

### Option 1: Beibehaltung und Reparatur des Custom-QSS
- **Vorteile:** SmartDesk behält einen einzigartigen, stark personalisierten Look.
- **Nachteile:** Extrem hoher Wartungsaufwand. Jedes neue Widget muss im CSS manuell bedacht werden, da native Fallbacks oft visuell "ausbrechen". System-Features wie Snap-Layouts in Windows 11 funktionieren mit rahmenlosen Qt-Fenstern teilweise nur eingeschränkt.

### Option 2: Nutzung eines etablierten PySide-Themes (z.B. qdarktheme)
- **Vorteile:** Professioneller Dark-Mode ohne den Wartungsaufwand von eigenem CSS.
- **Nachteile:** Erfordert eine externe Abhängigkeit. Ändert das Look & Feel abseits des gewohnten Windows-Standards.

## Entscheidung

**Wir haben uns entschieden, jegliches Custom-CSS (`style.qss`) zu leeren und auf den nativen Betriebssystem-Look von PySide6/Windows zurückzufallen.**

Begründung:
- **Wartbarkeit:** Der Verzicht auf Custom-Stylesheets eliminiert hunderte Zeilen an fehleranfälligem Design-Code. Die Applikation skaliert und rendert automatisch korrekt, basierend auf den System-Einstellungen des Benutzers.
- **Konsistenz:** Da SmartDesk ein tief ins System integriertes Tool ist (Registry-Modifikationen, Explorer-Restarts), sollte es sich visuell wie eine native System-Anwendung verhalten und anfühlen, anstatt wie eine abgesetzte Web-App.
- **Stabilität:** Wir haben das Flag `Qt.WA_TranslucentBackground` entfernt, um zu verhindern, dass Fenster ohne Custom-Style komplett unsichtbar rendern. Die rahmenlosen Eigenschaften (`Qt.FramelessWindowHint`) für die speziellen Floating-Panels (Control Panel, Overview) haben wir jedoch beibehalten.

## Konsequenzen

### Positive Folgen
- Massiv reduzierter Codebase-Footprint.
- Robusteres Rendering-Verhalten.
- Vertraute UI für Windows-Nutzer (inklusive nativen Checkboxen, Input-Feldern und Buttons).

### Negative Folgen / Risiken
- Verlust der einzigartigen "Brand-Identity" der grafischen Benutzeroberfläche.
- Der Dark-Mode ist nicht mehr erzwungen, sondern hängt vom Rendering-Engine-Standard des Systems bzw. von PySide6 ab.