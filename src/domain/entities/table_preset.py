"""
Domain entity for TablePreset.
This is a pure domain model without any external dependencies.
"""
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class TablePreset:
    """
    Represents a configuration preset for the game table.
    
    Attributes:
        id: Unique identifier for the preset.
        name: Name of the preset.
        points: List of (x, y) points defining the table.
        colors: HSV color values for the table (OpenCV format).
        min_area_threshold: Minimum area threshold for detection.
    """
    id: int
    name: str
    points: List[Tuple[int, int]]
    colors: List[Tuple[int, int, int]]
    min_area_threshold: int
