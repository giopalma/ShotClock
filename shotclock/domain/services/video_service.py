"""
Service interface (port) for Video operations.
This defines the contract that infrastructure adapters must implement.
"""
from abc import ABC, abstractmethod
from typing import Any, Callable
from shotclock.domain.entities.table_preset import TablePreset


class VideoService(ABC):
    """
    Abstract service interface for Video processing operations.
    
    This is a port in the Clean Architecture - it defines video operations
    without specifying implementation details.
    """
    
    @abstractmethod
    def get_frame(self) -> Any:
        """Get the current video frame."""
        pass
    
    @abstractmethod
    def start_motion_detection(
        self,
        table: TablePreset,
        start_callback: Callable[[], None],
        stop_callback: Callable[[], None],
    ) -> None:
        """Start motion detection with callbacks."""
        pass
    
    @abstractmethod
    def pause_motion_detection(self) -> None:
        """Pause motion detection."""
        pass
    
    @abstractmethod
    def resume_motion_detection(self) -> None:
        """Resume motion detection."""
        pass
    
    @abstractmethod
    def end_motion_detection(self) -> None:
        """End motion detection."""
        pass
