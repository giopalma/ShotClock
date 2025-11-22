"""
Repository interface (port) for TablePreset.
This defines the contract that infrastructure adapters must implement.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from shotclock.domain.entities.table_preset import TablePreset


class TablePresetRepository(ABC):
    """
    Abstract repository interface for TablePreset entities.
    
    This is a port in the Clean Architecture - it defines what operations
    are available but not how they are implemented.
    """
    
    @abstractmethod
    def get(self, preset_id: int) -> Optional[TablePreset]:
        """Retrieve a table preset by its ID."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[TablePreset]:
        """Retrieve all table presets."""
        pass
    
    @abstractmethod
    def create(
        self,
        name: str,
        points: List[Tuple[int, int]],
        colors: List[Tuple[int, int, int]],
        min_area_threshold: int,
    ) -> TablePreset:
        """Create a new table preset."""
        pass
    
    @abstractmethod
    def delete(self, preset_id: int) -> bool:
        """Delete a table preset by its ID. Returns True if successful."""
        pass
