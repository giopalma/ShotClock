from dataclasses import dataclass
from typing import List, Tuple
import json
from database import DatabaseConnection


@dataclass
class Preset:
    """Classe che rappresenta un preset di configurazione per il tavolo da gioco"""

    id: int
    name: str
    points: List[Tuple[int, int]]  # (x, y) punti del tavolo
    table_colors: List[
        Tuple[int, int, int]
    ]  # HSV (OpenCV format) per il colore del tavolo


class PresetRepository:
    _instance = None

    def __new__(cls, connection: DatabaseConnection):
        if cls._instance is None:
            cls._instance = super(PresetRepository, cls).__new__(cls)
            cls._instance.connection = connection.get_connection()
            cls._instance._initialize_debug_data()
        return cls._instance

    def _initialize_debug_data(self) -> None:
        cursor = self._instance.connection.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS preset (id INTEGER PRIMARY KEY, name TEXT, points, table_colors)"
        )
        cursor.execute(
            "INSERT INTO preset VALUES (0, 'Default', json('[[120, 80], [520, 80], [520, 280], [120, 280]]'), json('[[96, 180, 237], [98, 207, 181], [98, 215, 162], [98, 193, 243], [99, 237, 158]]'))"
        )
        self._instance.connection.commit()

    def save_preset(self, preset: Preset) -> None:
        """Salva un preset nel database"""
        pass

    def get_default_preset(self) -> Preset:
        """Recupera il preset di avvio dal database"""
        cursor = self._instance.connection.cursor()
        cursor.execute("SELECT * FROM preset WHERE id = 0")
        row = cursor.fetchone()
        id = row[0]
        name = row[1]
        points = json.loads(row[2])
        table_colors = json.loads(row[3])
        return Preset(id, name, points, table_colors)

    def get_preset_by_id(self, preset_id: int) -> Preset:
        """Recupera un preset dal database per ID"""
        cursor = self.connection.cursor()
