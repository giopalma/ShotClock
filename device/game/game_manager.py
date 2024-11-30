from .game import Game


class GameManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GameManager, cls).__new__(cls, *args, **kwargs)
            cls.game = None
        return cls._instance

    def get_game(self) -> Game:
        return self.game
