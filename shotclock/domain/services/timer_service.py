"""
Service interface (port) for Timer operations.
This defines the contract that infrastructure adapters must implement.
"""
from abc import ABC, abstractmethod
from typing import Callable


class TimerService(ABC):
    """
    Abstract service interface for Timer operations.
    
    This is a port in the Clean Architecture - it defines timer operations
    without specifying implementation details.
    """
    
    @abstractmethod
    def create_timer(
        self,
        duration: int,
        allarm_time: int,
        callback: Callable[[], None],
        allarm_callback: Callable[[], None],
        periodic_callback: Callable[[float, bool], None],
        periodic_time: int = 1,
    ) -> "Timer":
        """Create a new timer with specified parameters."""
        pass
    
    @abstractmethod
    def start_timer(self, timer: "Timer") -> None:
        """Start the timer."""
        pass
    
    @abstractmethod
    def pause_timer(self, timer: "Timer") -> float:
        """Pause the timer and return remaining time."""
        pass
    
    @abstractmethod
    def resume_timer(self, timer: "Timer") -> float:
        """Resume the timer and return remaining time."""
        pass
    
    @abstractmethod
    def end_timer(self, timer: "Timer") -> None:
        """End the timer."""
        pass
    
    @abstractmethod
    def add_time(self, timer: "Timer", time: float) -> None:
        """Add time to the timer."""
        pass
