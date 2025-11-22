"""
Service interface (port) for Notification operations.
This defines the contract that infrastructure adapters must implement.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class NotificationService(ABC):
    """
    Abstract service interface for sending notifications (e.g., WebSocket, sound).
    
    This is a port in the Clean Architecture - it defines notification operations
    without specifying implementation details.
    """
    
    @abstractmethod
    def emit(self, event: str, data: Any) -> None:
        """Emit a notification event with data."""
        pass
    
    @abstractmethod
    def emit_timer_update(self, remaining_time: float, status: str) -> None:
        """Emit a timer update notification."""
        pass
    
    @abstractmethod
    def emit_game_status(self, status: str) -> None:
        """Emit a game status notification."""
        pass
    
    @abstractmethod
    def play_alarm(self, is_final: bool = False) -> None:
        """Play an alarm sound."""
        pass
