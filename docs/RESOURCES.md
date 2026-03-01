# Ressourcen und Danksagung

Dieses Dokument listet die externen Bibliotheken, Werkzeuge und Technologien auf, die für die Entwicklung von SmartDesk verwendet werden.

## 1. Hauptbibliotheken (Python)

SmartDesk baut auf einer Reihe von leistungsstarken Open-Source-Python-Bibliotheken auf.

- **[PySide6](https://pypi.org/project/PySide6/)**
  - **Zweck:** Das offizielle Python-Binding für das Qt-Framework. Es ist die Grundlage für die gesamte grafische Benutzeroberfläche (GUI) von SmartDesk.

- **[psutil](https://pypi.org/project/psutil/)**
  - **Zweck:** Eine plattformübergreifende Bibliothek zum Auslesen von Systeminformationen und zur Prozessverwaltung. SmartDesk nutzt sie für den effizienten Neustart des `explorer.exe`-Prozesses.

- **[pywin32](https://pypi.org/project/pywin32/)**
  - **Zweck:** Bietet Zugriff auf weite Teile der Windows-API. Unverzichtbar für systemnahe Operationen wie das Modifizieren der Registry und die Interaktion mit Fenster-Handles.

- **[pynput](https://pypi.org/project/pynput/)**
  - **Zweck:** Dient zur Überwachung und Steuerung von Eingabegeräten. SmartDesk verwendet diese Bibliothek, um die globalen Hotkeys zu registrieren und darauf zu reagieren.

- **[pystray](https://pypi.org/project/pystray/)**
  - **Zweck:** Eine einfache Bibliothek zum Erstellen von System-Tray-Icons unter Windows, macOS und Linux. In SmartDesk erstellt sie das Icon im Infobereich der Taskleiste.

- **[Pillow](https://pypi.org/project/Pillow/)**
  - **Zweck:** Ein Fork der Python Imaging Library (PIL), der umfangreiche Bildverarbeitungsfunktionen bietet. Wird zur Handhabung von Hintergrundbildern und Icons verwendet.

- **[Colorama](https://pypi.org/project/colorama/)**
  - **Zweck:** Wird genutzt, um farbige Ausgaben im Kommandozeilen-Interface (CLI) zu erzeugen und die Lesbarkeit zu verbessern.

## 2. Entwicklungswerkzeuge und Plattformen

- **[Python](https://www.python.org/)**
  - Die Programmiersprache, in der SmartDesk geschrieben ist.

- **[Git](https://git-scm.com/)** & **[GitHub](https://github.com/)**
  - Git wird für die Versionskontrolle des Quellcodes verwendet. GitHub dient als Plattform für das Hosting des Repositories.

- **[Ruff](https://astral.sh/ruff)**
  - Ein extrem schneller Python-Linter und -Formatter, der zur Sicherstellung der Code-Qualität und eines einheitlichen Stils im Projekt eingesetzt wird.

## 3. Kerntechnologien

- **[Windows API](https://learn.microsoft.com/en-us/windows/win32/api/)**
  - Die native Programmierschnittstelle von Microsoft Windows ist das Fundament von SmartDesk. Viele Kernfunktionen, wie das Ändern des Desktops, das Setzen von Hintergrundbildern und die Manipulation von Icons, wären ohne den direkten Aufruf von WinAPI-Funktionen nicht möglich.
