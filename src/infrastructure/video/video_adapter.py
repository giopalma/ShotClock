"""
Video adapter implementation.
This wraps the existing VideoProducer and VideoConsumer as a service adapter.
"""
from typing import Any, Callable, Optional
from src.domain.services.video_service import VideoService
from src.domain.entities.table_preset import TablePreset


class VideoAdapter(VideoService):
    """
    Video service adapter.
    
    This implements the VideoService interface using the existing
    VideoProducer and VideoConsumer infrastructure.
    """
    
    def __init__(self, video_producer):
        """
        Initialize the video adapter.
        
        Args:
            video_producer: VideoProducer instance from device.video_producer
        """
        self.video_producer = video_producer
        self.video_consumer = None
    
    def get_frame(self) -> Any:
        """Get the current video frame."""
        return self.video_producer.get_frame()
    
    def start_motion_detection(
        self,
        table: TablePreset,
        start_callback: Callable[[], None],
        stop_callback: Callable[[], None],
    ) -> None:
        """
        Start motion detection with callbacks.
        
        This creates and starts a VideoConsumer instance.
        """
        # Import here to avoid circular dependencies
        from device.game.video_consumer import VideoConsumer
        
        self.video_consumer = VideoConsumer(
            table=table,
            video_producer=self.video_producer,
            start_movement_callback=start_callback,
            stop_movement_callback=stop_callback,
        )
        self.video_consumer.start()
    
    def pause_motion_detection(self) -> None:
        """Pause motion detection."""
        if self.video_consumer:
            self.video_consumer.pause()
    
    def resume_motion_detection(self) -> None:
        """Resume motion detection."""
        if self.video_consumer:
            self.video_consumer.resume()
    
    def end_motion_detection(self) -> None:
        """End motion detection."""
        if self.video_consumer:
            self.video_consumer.end()
            self.video_consumer = None
