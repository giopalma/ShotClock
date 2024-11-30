from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class TablePreset:
    """Classe che rappresenta un preset di configurazione per il tavolo da gioco"""

    id: int
    name: str
    points: List[Tuple[int, int]]  # (x, y) punti del tavolo
    table_colors: List[
        Tuple[int, int, int]
    ]  # HSV (OpenCV format) per il colore del tavolo
