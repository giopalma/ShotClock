"""
Timer adapter implementation.
This wraps the existing Timer implementation as a service adapter.
"""
import time
from threading import Lock, Thread, Event
import math
from typing import Callable
from src.domain.services.timer_service import TimerService


class Timer:
    """
    Timer implementation with alarm and periodic callbacks.
    """
    
    def __init__(
        self,
        duration: int,
        allarm_time: int,
        callback: Callable[[], None],
        allarm_callback: Callable[[], None],
        periodic_callback: Callable[[float, bool], None],
        periodic_time: int = 1,
    ):
        self.duration = duration
        self.remaining_time = duration
        self._remaining_time_lock = Lock()
        self.callback = callback
        self.allarm_time = allarm_time
        self.allarm_callback = allarm_callback
        self.periodic_callback = periodic_callback
        self.periodic_time = periodic_time
        self._allarm_triggered = False
        self._countdown_triggered = False
        self._last_countdown_second = 6
        self._is_running_event = Event()
        self._end_event = Event()
        self.thread = None

    def _run(self):
        """Execute the countdown timer."""
        time.sleep(2)
        _last_time_check = time.monotonic()
        while (not self._end_event.is_set()) and (self.remaining_time > 0):
            start_time = time.monotonic()
            if not self._is_running_event.is_set():
                self._is_running_event.wait()
                start_time = time.monotonic()

            if self._end_event.is_set():
                break
            time.sleep(max(0.001, min(self.remaining_time / 10, 0.1)))

            elapsed = time.monotonic() - start_time
            with self._remaining_time_lock:
                self.remaining_time = max(0, self.remaining_time - elapsed)

            current_time = time.monotonic()
            if current_time - _last_time_check >= self.periodic_time:
                self.periodic_callback(
                    self.remaining_time, self._is_running_event.is_set()
                )
                _last_time_check = current_time

            if self.remaining_time <= self.allarm_time and not self._allarm_triggered:
                self.allarm_callback()
                self._allarm_triggered = True

            # Final countdown alarm (5,4,3,2,1)
            current_second = math.ceil(self.remaining_time)
            if (
                current_second <= 5
                and current_second > 0
                and current_second < self._last_countdown_second
            ):
                self._last_countdown_second = current_second
                self.allarm_callback()

            elif self.remaining_time <= 0:
                self.callback()

    def start(self):
        """Start the timer."""
        self._is_running_event.set()
        self.thread = Thread(target=self._run, daemon=False)
        self.thread.name = "TimerThread"
        self.thread.start()

    def add_time(self, time_amount: float):
        """Add time to the timer."""
        with self._remaining_time_lock:
            self.remaining_time = self.remaining_time + time_amount
        self.periodic_callback(self.remaining_time, self._is_running_event.is_set())

    def pause(self) -> float:
        """Pause the timer."""
        self._is_running_event.clear()
        return self.remaining_time

    def resume(self) -> float:
        """Resume the timer from pause."""
        self._is_running_event.set()
        return self.remaining_time

    def end(self):
        """Stop the timer."""
        if self.thread and self.thread.is_alive():
            self._end_event.set()
            self._is_running_event.set()


class TimerAdapter(TimerService):
    """
    Timer service adapter.
    
    This implements the TimerService interface using the Timer class.
    """
    
    def create_timer(
        self,
        duration: int,
        allarm_time: int,
        callback: Callable[[], None],
        allarm_callback: Callable[[], None],
        periodic_callback: Callable[[float, bool], None],
        periodic_time: int = 1,
    ) -> Timer:
        """Create a new timer with specified parameters."""
        return Timer(
            duration=duration,
            allarm_time=allarm_time,
            callback=callback,
            allarm_callback=allarm_callback,
            periodic_callback=periodic_callback,
            periodic_time=periodic_time,
        )
    
    def start_timer(self, timer: Timer) -> None:
        """Start the timer."""
        timer.start()
    
    def pause_timer(self, timer: Timer) -> float:
        """Pause the timer and return remaining time."""
        return timer.pause()
    
    def resume_timer(self, timer: Timer) -> float:
        """Resume the timer and return remaining time."""
        return timer.resume()
    
    def end_timer(self, timer: Timer) -> None:
        """End the timer."""
        timer.end()
    
    def add_time(self, timer: Timer, time_amount: float) -> None:
        """Add time to the timer."""
        timer.add_time(time_amount)
