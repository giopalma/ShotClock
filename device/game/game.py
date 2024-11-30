from typing import Literal
from .timer import Timer


class Game:
    def __init__(self, turn_duration: int):
        self.turn_duration = turn_duration
        self.current_player = 1
        self.timers = {1: None, 2: None}
        self.status: Literal["ready", "running", "waiting", "ended"] = "ready"

    def start_turn(self):
        """Inizia il turno per il giocatore corrente e avvia il timer."""
        self.stop_timer(self.current_player)  # Fermo eventuali timer precedenti
        self.timers[self.current_player] = Timer(self.turn_duration, self.end_turn)
        self.timers[self.current_player].start()

    def end_turn(self):
        """Termina il turno corrente e passa al giocatore successivo."""
        self.stop_timer(self.current_player)
        self.current_player = 2 if self.current_player == 1 else 1
        self.start_turn()

    def stop_timer(self, player):
        if self.timers[player]:
            self.timers[player].cancel()
            self.timers[player] = None

    def stop_game(self):
        """Ferma il gioco e cancella tutti i timer."""
        self.stop_timer(1)
        self.stop_timer(2)
        print("Gioco terminato.")
