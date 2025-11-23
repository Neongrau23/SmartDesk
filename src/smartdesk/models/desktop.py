# Dateipfad: src/smartdesk/models/desktop.py

from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class IconPosition:
    """
    Repräsentiert die Position eines einzelnen Desktop-Icons.
    Dies ist unser Datenmodell für ein Icon.
    """
    name: str
    x: int
    y: int
    
    def to_dict(self) -> dict:
        """Konvertiert das Icon-Objekt in ein Dictionary für JSON."""
        return {"name": self.name, "x": self.x, "y": self.y}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'IconPosition':
        """Erstellt ein Icon-Objekt aus einem Dictionary."""
        return cls(name=data["name"], x=data["x"], y=data["y"])


@dataclass
class Desktop:
    """
    Repräsentiert einen kompletten Desktop mit Pfad und Icons.
    """
    name: str
    path: str
    is_active: bool = False
    
    # NEU: Eine Liste, die alle IconPosition-Objekte für diesen Desktop speichert.
    # default_factory=list stellt sicher, dass jeder neue Desktop eine leere Liste erhält.
    icon_positionen: List[IconPosition] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert das Desktop-Objekt für die JSON-Speicherung."""
        return {
            "name": self.name,
            "path": self.path,
            "is_active": self.is_active,
            
            # NEU: Wir wandeln jedes Icon-Objekt in ein Dictionary um
            # und speichern die Liste im JSON.
            "icon_positionen": [icon.to_dict() for icon in self.icon_positionen]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Desktop':
        """Erstellt ein Desktop-Objekt aus den JSON-Daten."""
        
        # NEU: Wir lesen die Liste der Icons aus dem JSON.
        # .get("icon_positionen", []) sorgt dafür, dass es nicht abstürzt,
        # falls ein alter Desktop-Eintrag noch keine Icons hat.
        icons_data = data.get("icon_positionen", [])
        icons = [IconPosition.from_dict(icon_data) for icon_data in icons_data]
        
        return cls(
            name=data["name"],
            path=data["path"],
            is_active=data.get("is_active", False),
            icon_positionen=icons  # NEU: Die geladenen Icons zuweisen
        )
    