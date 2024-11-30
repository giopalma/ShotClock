class VideoProcessor:
    # Singleton di VideoProcessor
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(VideoProcessor, cls).__new__(cls, *args, **kwargs)
            cls.frame = None
        return cls._instance
