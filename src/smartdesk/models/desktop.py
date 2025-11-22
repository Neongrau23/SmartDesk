from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Desktop:
    name: str
    path: str
    is_active: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert das Objekt für die JSON-Speicherung."""
        return {
            "name": self.name,
            "path": self.path,
            "is_active": self.is_active
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Desktop':
        """Erstellt ein Objekt aus den JSON-Daten."""
        return cls(
            name=data["name"],
            path=data["path"],
            is_active=data.get("is_active", False)
        )
        