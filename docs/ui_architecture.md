# UI Architektur & Entwicklung

Dieses Dokument beschreibt den Aufbau der Benutzeroberfläche (GUI) von SmartDesk (ab Version 0.2.0).
Die Anwendung basiert auf **PySide6** (Qt for Python) und nutzt eine **Single-Window-Architektur**.

## 📂 Struktur

Die UI-Dateien befinden sich in `src/smartdesk/ui/gui/`:

```text
src/smartdesk/ui/gui/
├── gui_main.py           # Hauptfenster & Entry Point. Verwaltet Navigation & Window-State.
├── style.qss             # Globales Stylesheet (CSS-ähnlich) für das Design.
├── designer/             # .ui Dateien für das Hauptfenster (Sidebar etc.)
│   └── main.ui
└── pages/                # Einzelne Inhaltsseiten (Content Pages)
    ├── desktop_page.py   # Logik für die Desktop-Verwaltung
    └── ui/               # .ui Dateien für die Pages
        └── desktop_page.ui
```

## 🎨 Design-Konzept

### 1. Single-Window
Statt viele Fenster zu öffnen, gibt es ein Hauptfenster (`SmartDeskMainWindow`).
Im Zentrum befindet sich ein `QStackedWidget`, das verschiedene "Pages" (Widgets) anzeigt.
Über die Sidebar (Buttons links) wird der Index des `QStackedWidget` gewechselt.

### 2. Styling (Theming)
Das Design ist **zentralisiert** in `style.qss`.
*   **Wichtig:** In den `.ui` Dateien (Qt Designer) sollten **keine** `styleSheet`-Properties gesetzt werden, da diese das globale QSS überschreiben würden.
*   Das Theme ist ein "Modern Dark Theme" mit der Akzentfarbe Blau (`#0078d4`) und Dunkelgrau (`#1e1e1e`).

**Wichtige CSS-Klassen/IDs:**
*   `QPushButton.primary-btn`: Blauer Haupt-Button.
*   `QPushButton.nav-btn`: Buttons in der Sidebar.
*   `QLabel.page-title`: Große Überschriften.
*   `#btn_edit_name`: Spezieller Style für den Umbenennen-Button.

## 🛠 Workflow: Neue Seite hinzufügen

Möchtest du einen neuen Reiter (z.B. "Statistiken") hinzufügen, folge diesen Schritten:

### 1. UI erstellen
Erstelle eine neue `.ui` Datei in `src/smartdesk/ui/gui/pages/ui/` (z.B. `stats_page.ui`) mit dem Qt Designer.
*   Verwende ein `QWidget` als Basis.
*   Vergib sinnvolle `objectName`s für Widgets (z.B. `lbl_title`, `btn_refresh`).

### 2. Logik-Klasse erstellen
Erstelle eine Python-Datei in `src/smartdesk/ui/gui/pages/` (z.B. `stats_page.py`).

**Boilerplate Code:**
```python
import os
from PySide6.QtWidgets import QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice

class StatsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.load_ui()
        # self.setup_connections()

    def load_ui(self):
        loader = QUiLoader()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "ui", "stats_page.ui")
        
        ui_file = QFile(ui_path)
        if not ui_file.open(QIODevice.ReadOnly):
            print(f"Error: {ui_path} not found")
            return
            
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        
        # Layout Hack für eingebettete Widgets
        layout = self.layout()
        if not layout:
            from PySide6.QtWidgets import QVBoxLayout
            layout = QVBoxLayout(self)
            self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        
        # Elemente finden
        # self.btn_refresh = self.ui.findChild(QPushButton, "btn_refresh")
```

### 3. In Hauptfenster registrieren
Öffne `src/smartdesk/ui/gui/gui_main.py`:

1.  Importiere die neue Seite:
    ```python
    from smartdesk.ui.gui.pages.stats_page import StatsPage
    ```

2.  Initialisiere sie in `setup_pages(self)`:
    ```python
    self.page_stats = StatsPage()
    self.stacked_widget.addWidget(self.page_stats)
    ```

3.  Button verbinden in `setup_connections(self)`:
    *   (Stelle sicher, dass in `main.ui` ein Button dafür existiert, z.B. `btn_nav_stats`)
    ```python
    self.btn_stats.clicked.connect(self.show_stats)
    ```

4.  Zeige-Methode erstellen:
    ```python
    def show_stats(self):
        self.stacked_widget.setCurrentWidget(self.page_stats)
    ```

## 💡 Best Practices

*   **Services nutzen:** Die UI sollte keine Geschäftslogik enthalten (keine Dateien schreiben, keine Registry ändern). Rufe stattdessen Funktionen aus `smartdesk.core.services` auf.
*   **Logging:** Nutze `logger.debug()` für UI-Events und `logger.error()` für Fehler.
*   **Fehlerbehandlung:** Fange Exceptions ab und zeige dem Nutzer `QMessageBox` Fehler an, statt die App abstürzen zu lassen.
*   **Icons:** Nutze Unicode-Zeichen oder lade SVGs für Buttons, um externe Abhängigkeiten gering zu halten.

## ⚠️ Wichtig: Layouts & Naming

Damit die UI sauber skaliert und im Code leicht ansprechbar ist:

1.  **Layouts verwenden:**
    *   Ziehe Widgets nie einfach nur auf das Formular.
    *   Nutze immer Layouts (Rechtsklick auf Hintergrund -> *Lay out* -> *Lay out Vertically/Horizontally*).
    *   Wenn sich ein Fenster nicht vergrößern lässt, fehlt meist das Top-Level-Layout.

2.  **Naming Conventions (objectName):**
    *   Vergebe im Qt Designer sinnvolle Namen für Elemente, die du im Code brauchst:
    *   `btn_action` (Buttons, z.B. `btn_save`)
    *   `lbl_info` (Labels, die sich ändern, z.B. `lbl_status`)
    *   `inp_data` (Input fields, z.B. `inp_name`)
    *   `list_items` (Listen)
    *   Statische Labels (nur Text) brauchen keinen speziellen Namen.
