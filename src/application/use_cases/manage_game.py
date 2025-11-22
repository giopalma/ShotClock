"""
Use case for managing game lifecycle (start, pause, resume, end).
This contains the application-specific business logic.
"""
from typing import Optional
from src.domain.entities.game import Game
from src.domain.entities.ruleset import Ruleset
from src.domain.entities.table_preset import TablePreset
from src.domain.repositories.ruleset_repository import RulesetRepository
from src.domain.repositories.table_preset_repository import TablePresetRepository
from src.domain.services.timer_service import TimerService
from src.domain.services.video_service import VideoService
from src.domain.services.notification_service import NotificationService


class ManageGameUseCase:
    """
    Use case for managing the game lifecycle.
    
    This encapsulates the business logic for starting, pausing,
    resuming, and ending a game.
    """
    
    def __init__(
        self,
        ruleset_repository: RulesetRepository,
        table_preset_repository: TablePresetRepository,
        timer_service: TimerService,
        video_service: VideoService,
        notification_service: NotificationService,
    ):
        self.ruleset_repository = ruleset_repository
        self.table_preset_repository = table_preset_repository
        self.timer_service = timer_service
        self.video_service = video_service
        self.notification_service = notification_service
        self._current_timer = None
        self._current_video_consumer = None
    
    def start_game(self, game: Game) -> Optional[str]:
        """
        Start the game.
        
        Args:
            game: The game entity to start.
            
        Returns:
            Error message if game cannot be started, None otherwise.
        """
        if game.status != "ready":
            return "Game already started."
        
        ruleset = self.ruleset_repository.get(game.ruleset_id)
        table_preset = self.table_preset_repository.get(game.table_preset_id)
        
        if not ruleset or not table_preset:
            return "Invalid ruleset or table preset."
        
        game.status = "running"
        
        # Start video motion detection
        self.video_service.start_motion_detection(
            table=table_preset,
            start_callback=lambda: self._handle_movement_start(game),
            stop_callback=lambda: self._handle_movement_stop(game, ruleset),
        )
        
        # Start the first turn
        self._start_turn(game, ruleset)
        
        # Notify game started
        self.notification_service.emit_game_status("started")
        
        return None
    
    def pause_game(self, game: Game) -> Optional[str]:
        """
        Pause the game.
        
        Args:
            game: The game entity to pause.
            
        Returns:
            Error message if game cannot be paused, None otherwise.
        """
        if game.status != "running":
            return "Game is not running."
        
        remaining_time = self.timer_service.pause_timer(self._current_timer)
        self.video_service.pause_motion_detection()
        
        game.status = "paused"
        game.last_remaining_time = remaining_time
        
        self.notification_service.emit_timer_update(remaining_time, "paused")
        
        return None
    
    def resume_game(self, game: Game) -> Optional[str]:
        """
        Resume the game from pause.
        
        Args:
            game: The game entity to resume.
            
        Returns:
            Error message if game cannot be resumed, None otherwise.
        """
        if game.status != "paused":
            return "Game is not paused."
        
        remaining_time = self.timer_service.resume_timer(self._current_timer)
        self.video_service.resume_motion_detection()
        
        game.status = "running"
        game.last_remaining_time = remaining_time
        
        self.notification_service.emit_timer_update(remaining_time, "running")
        
        return None
    
    def end_game(self, game: Game) -> Optional[str]:
        """
        End the game.
        
        Args:
            game: The game entity to end.
            
        Returns:
            Error message if game cannot be ended, None otherwise.
        """
        if game.status == "ended":
            return "Game already ended."
        
        # Resume if paused to ensure clean shutdown
        if game.status == "paused":
            self.resume_game(game)
        
        if self._current_timer:
            self.timer_service.end_timer(self._current_timer)
        
        self.video_service.end_motion_detection()
        
        game.status = "ended"
        
        self.notification_service.emit_game_status("ended")
        
        return None
    
    def increment_time(self, game: Game, player: int) -> Optional[str]:
        """
        Add increment time for a player.
        
        Args:
            game: The game entity.
            player: Player index (0 or 1).
            
        Returns:
            Error message if increment cannot be applied, None otherwise.
        """
        if game.status != "running":
            return "Game is not running."
        
        if game.increments[player] <= 0:
            return f"No increments available for player: {game.player_names[player]}"
        
        ruleset = self.ruleset_repository.get(game.ruleset_id)
        if not ruleset:
            return "Invalid ruleset."
        
        game.increments[player] -= 1
        self.timer_service.add_time(self._current_timer, ruleset.increment_duration)
        
        return None
    
    def next_turn(self, game: Game) -> None:
        """
        Move to the next turn.
        
        Args:
            game: The game entity.
        """
        if game.status != "running":
            return
        
        ruleset = self.ruleset_repository.get(game.ruleset_id)
        if not ruleset:
            return
        
        if self._current_timer:
            self.timer_service.end_timer(self._current_timer)
        
        self._start_turn(game, ruleset)
    
    def _start_turn(self, game: Game, ruleset: Ruleset) -> None:
        """Start a new turn with a new timer."""
        duration = ruleset.initial_duration if game.status == "ready" else ruleset.turn_duration
        
        def time_up_callback():
            self.notification_service.play_alarm(is_final=True)
            self.next_turn(game)
        
        def allarm_callback():
            self.notification_service.play_alarm(is_final=False)
        
        def periodic_callback(remaining_time: float, is_running: bool):
            game.last_remaining_time = remaining_time
            status = "running" if is_running else "paused"
            self.notification_service.emit_timer_update(remaining_time, status)
        
        self._current_timer = self.timer_service.create_timer(
            duration=duration,
            allarm_time=ruleset.allarm_time,
            callback=time_up_callback,
            allarm_callback=allarm_callback,
            periodic_callback=periodic_callback,
            periodic_time=1,
        )
        
        self.timer_service.start_timer(self._current_timer)
    
    def _handle_movement_start(self, game: Game) -> None:
        """Handle when movement is detected."""
        if game.status == "running":
            game.status = "waiting"
            remaining_time = self.timer_service.pause_timer(self._current_timer)
            self.notification_service.emit_timer_update(remaining_time, "paused")
    
    def _handle_movement_stop(self, game: Game, ruleset: Ruleset) -> None:
        """Handle when movement stops."""
        if game.status == "waiting":
            game.status = "running"
            self.next_turn(game)
