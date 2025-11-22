"""
Dependency Injection Container.
This configures and provides all dependencies for the application.
"""
from typing import Optional
from flask_sqlalchemy import SQLAlchemy

from shotclock.domain.repositories.ruleset_repository import RulesetRepository
from shotclock.domain.repositories.table_preset_repository import TablePresetRepository
from shotclock.domain.services.timer_service import TimerService
from shotclock.domain.services.video_service import VideoService
from shotclock.domain.services.notification_service import NotificationService

from shotclock.application.use_cases.create_game import CreateGameUseCase
from shotclock.application.use_cases.manage_game import ManageGameUseCase

from shotclock.infrastructure.persistence.sqlalchemy_ruleset_repository import SQLAlchemyRulesetRepository
from shotclock.infrastructure.persistence.sqlalchemy_table_preset_repository import SQLAlchemyTablePresetRepository
from shotclock.infrastructure.hardware.timer_adapter import TimerAdapter
from shotclock.infrastructure.hardware.notification_adapter import NotificationAdapter
from shotclock.infrastructure.video.video_adapter import VideoAdapter


class DIContainer:
    """
    Dependency Injection Container.
    
    This container is responsible for creating and managing all dependencies,
    ensuring proper separation of concerns and testability.
    """
    
    def __init__(
        self,
        db: SQLAlchemy,
        video_producer,
        socketio=None,
    ):
        self.db = db
        self.video_producer = video_producer
        self.socketio = socketio
        
        # Repositories
        self._ruleset_repository: Optional[RulesetRepository] = None
        self._table_preset_repository: Optional[TablePresetRepository] = None
        
        # Services
        self._timer_service: Optional[TimerService] = None
        self._video_service: Optional[VideoService] = None
        self._notification_service: Optional[NotificationService] = None
        
        # Use Cases
        self._create_game_use_case: Optional[CreateGameUseCase] = None
        self._manage_game_use_case: Optional[ManageGameUseCase] = None
    
    # Repository providers
    
    def get_ruleset_repository(self) -> RulesetRepository:
        """Get or create RulesetRepository."""
        if not self._ruleset_repository:
            self._ruleset_repository = SQLAlchemyRulesetRepository(self.db)
        return self._ruleset_repository
    
    def get_table_preset_repository(self) -> TablePresetRepository:
        """Get or create TablePresetRepository."""
        if not self._table_preset_repository:
            self._table_preset_repository = SQLAlchemyTablePresetRepository(self.db)
        return self._table_preset_repository
    
    # Service providers
    
    def get_timer_service(self) -> TimerService:
        """Get or create TimerService."""
        if not self._timer_service:
            self._timer_service = TimerAdapter()
        return self._timer_service
    
    def get_video_service(self) -> VideoService:
        """Get or create VideoService."""
        if not self._video_service:
            self._video_service = VideoAdapter(self.video_producer)
        return self._video_service
    
    def get_notification_service(self) -> NotificationService:
        """Get or create NotificationService."""
        if not self._notification_service:
            self._notification_service = NotificationAdapter(self.socketio)
        return self._notification_service
    
    # Use Case providers
    
    def get_create_game_use_case(self) -> CreateGameUseCase:
        """Get or create CreateGameUseCase."""
        if not self._create_game_use_case:
            self._create_game_use_case = CreateGameUseCase(
                ruleset_repository=self.get_ruleset_repository(),
                table_preset_repository=self.get_table_preset_repository(),
            )
        return self._create_game_use_case
    
    def get_manage_game_use_case(self) -> ManageGameUseCase:
        """Get or create ManageGameUseCase."""
        if not self._manage_game_use_case:
            self._manage_game_use_case = ManageGameUseCase(
                ruleset_repository=self.get_ruleset_repository(),
                table_preset_repository=self.get_table_preset_repository(),
                timer_service=self.get_timer_service(),
                video_service=self.get_video_service(),
                notification_service=self.get_notification_service(),
            )
        return self._manage_game_use_case
    
    def cleanup(self):
        """Clean up resources."""
        if self._notification_service:
            if hasattr(self._notification_service, 'cleanup'):
                self._notification_service.cleanup()
