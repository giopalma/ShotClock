"""
Notification adapter implementation.
This handles WebSocket notifications and sound alarms.
"""
import time
import threading
from typing import Any, Optional
from shotclock.domain.services.notification_service import NotificationService


try:
    from gpiozero import Buzzer
    GPIOZERO_AVAILABLE = True
except ImportError:
    GPIOZERO_AVAILABLE = False


def is_raspberry_pi():
    """Check if running on Raspberry Pi."""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            return 'Raspberry Pi' in f.read()
    except:
        return False


class NotificationAdapter(NotificationService):
    """
    Notification service adapter.
    
    This implements the NotificationService interface using
    Flask-SocketIO for WebSocket and hardware buzzer or winsound for alarms.
    """
    
    TIME_SOUND_BUZZER = 0.5
    TIME_FINAL_BUZZER = 2.0
    
    def __init__(self, socketio=None):
        self.socketio = socketio
        self._is_raspberry_pi = is_raspberry_pi()
        self._buzzer = None
        
        if self._is_raspberry_pi and GPIOZERO_AVAILABLE:
            try:
                self._buzzer = Buzzer(11)
            except:
                self._buzzer = None
    
    def emit(self, event: str, data: Any) -> None:
        """Emit a notification event with data."""
        if self.socketio:
            self.socketio.emit(event, data)
    
    def emit_timer_update(self, remaining_time: float, status: str) -> None:
        """Emit a timer update notification."""
        if self.socketio:
            self.socketio.emit(
                "timer",
                {
                    "timestamp": time.time(),
                    "remaining_time": remaining_time,
                    "status": status,
                },
            )
    
    def emit_game_status(self, status: str) -> None:
        """Emit a game status notification."""
        if self.socketio:
            self.socketio.emit("game", status)
    
    def play_alarm(self, is_final: bool = False) -> None:
        """Play an alarm sound."""
        duration = self.TIME_FINAL_BUZZER if is_final else self.TIME_SOUND_BUZZER
        
        if self._is_raspberry_pi and self._buzzer:
            # Raspberry Pi with buzzer
            t = threading.Thread(target=self._play_buzzer, args=(duration,))
            t.start()
        else:
            # Fallback to winsound on Windows
            try:
                import winsound
                winsound.Beep(1000, int(1000 * duration))
            except ImportError:
                # No sound available
                pass
    
    def _play_buzzer(self, duration: float):
        """Play the buzzer for the specified duration."""
        if self._buzzer:
            self._buzzer.beep(on_time=duration, off_time=duration, n=1)
    
    def cleanup(self):
        """Clean up resources."""
        if self._buzzer:
            try:
                self._buzzer.off()
                self._buzzer.close()
            except:
                pass
