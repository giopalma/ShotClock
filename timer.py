import time
from enum import Enum


class Player(Enum):
    PLAYER1 = 1
    PLAYER2 = 2


class TurnTimer:
    def __init__(self, time_per_player_seconds=300):  # 5 minutes default per player
        self.time_per_player = time_per_player_seconds
        self.reset()

    def reset(self):
        """Reset all timer values to initial state"""
        self.player1_time = self.time_per_player
        self.player2_time = self.time_per_player
        self.current_player = Player.PLAYER1
        self.is_running = False
        self.last_update = None
        self.game_start_time = None

    def start(self):
        """Start or resume the timer"""
        if not self.is_running:
            self.is_running = True
            self.last_update = time.time()
            if not self.game_start_time:
                self.game_start_time = time.time()

    def stop(self):
        """Stop the timer"""
        if self.is_running:
            self._update_times()
            self.is_running = False

    def switch_player(self):
        """Switch to the other player"""
        if self.is_running:
            self._update_times()
        self.current_player = (
            Player.PLAYER2 if self.current_player == Player.PLAYER1 else Player.PLAYER1
        )
        self.last_update = time.time()

    def _update_times(self):
        """Update the time for the current player"""
        if not self.last_update:
            return

        elapsed = time.time() - self.last_update
        if self.current_player == Player.PLAYER1:
            self.player1_time -= elapsed
        else:
            self.player2_time -= elapsed
        self.last_update = time.time()

    def get_current_player_time(self):
        """Get remaining time for current player in seconds"""
        if self.is_running:
            self._update_times()
        return (
            self.player1_time
            if self.current_player == Player.PLAYER1
            else self.player2_time
        )

    def get_player_time(self, player):
        """Get remaining time for specified player in seconds"""
        if self.is_running:
            self._update_times()
        return self.player1_time if player == Player.PLAYER1 else self.player2_time

    def get_game_time(self):
        """Get total game time in seconds"""
        if not self.game_start_time:
            return 0
        return time.time() - self.game_start_time

    def is_game_over(self):
        """Check if either player has run out of time"""
        return self.player1_time <= 0 or self.player2_time <= 0

    def get_winner(self):
        """Get the winner if game is over, None otherwise"""
        if not self.is_game_over():
            return None
        if self.player1_time <= 0:
            return Player.PLAYER2
        return Player.PLAYER1
