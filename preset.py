from dataclasses import dataclass
from typing import List, Tuple

from database import DatabaseConnection


@dataclass
class Preset:
    """Classe che rappresenta un preset di configurazione per il tavolo da gioco"""

    id: int
    name: str
    frame: List[Tuple[int, int]]  # (x, y) punti del tavolo

    colors: List[str]  # RGB values


class PresetRepository:
    def __init__(self, connection: DatabaseConnection):
        self.connection = connection

    def save_preset(self, preset: Preset) -> None:
        """Salva un preset nel database"""
        pass

    def get_default_preset(self) -> Preset:
        """Recupera il preset di avvio dal database"""
        pass

    def get_preset_by_id(self, preset_id: int) -> Preset:
        """Recupera un preset dal database per ID"""
        cursor = self.connection.cursor()
