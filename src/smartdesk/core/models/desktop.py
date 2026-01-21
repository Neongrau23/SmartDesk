# Dateipfad: src/smartdesk/core/models/desktop.py

from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class IconPosition:
    """
    Repräsentiert die Position eines einzelnen Desktop-Icons.
    Dies ist unser Datenmodell für ein Icon.
    """

    index: int
    name: str
    x: int
    y: int

    def to_dict(self) -> dict:
        """Konvertiert das Icon-Objekt in ein Dictionary für JSON."""
        return {"index": self.index, "name": self.name, "x": self.x, "y": self.y}

    @classmethod
    def from_dict(cls, data: dict) -> "IconPosition":
        """Erstellt ein Icon-Objekt aus einem Dictionary."""
        return cls(index=data.get("index", 0), name=data["name"], x=data["x"], y=data["y"])


@dataclass
class Desktop:
    """
    Repräsentiert einen kompletten Desktop mit Pfad und Icons.
    """

    name: str
    path: str
    is_active: bool = False
    wallpaper_path: str = ""
    icon_positionen: List[IconPosition] = field(default_factory=list)
    protected: bool = False  # Geschützt vor Löschen/Bearbeiten (z.B. Original Desktop)
    created_at: str = ""  # ISO-Format Zeitstempel der Erstellung

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert das Desktop-Objekt für die JSON-Speicherung."""
        return {
            "name": self.name,
            "path": self.path,
            "is_active": self.is_active,
            "wallpaper_path": self.wallpaper_path,
            "icon_positionen": [icon.to_dict() for icon in self.icon_positionen],
            "protected": self.protected,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Desktop":
        """Erstellt ein Desktop-Objekt aus den JSON-Daten."""
        icons_data = data.get("icon_positionen", [])
        icons = [IconPosition.from_dict(icon_data) for icon_data in icons_data]

        return cls(
            name=data["name"],
            path=data["path"],
            is_active=data.get("is_active", False),
            wallpaper_path=data.get("wallpaper_path", ""),
            icon_positionen=icons,
            protected=data.get("protected", False),
            created_at=data.get("created_at", ""),
        )

    def is_protected(self) -> bool:
        """Prüft ob der Desktop geschützt ist."""
        return self.protected
