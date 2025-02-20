from typing import Literal

from video_consumer import VideoConsumer
from ruleset import Ruleset
from .timer import Timer

class Game:

    def __init__(self, ruleset: Ruleset, player1_name: str, player2_name:str):
        """
        Scrivere il doc della classe Game
        """
        self.ruleset = ruleset
        self.player_names = [player1_name, player2_name]
        self.current_player = 1
        self.remaining_increments = [ruleset.max_increment_for_match, ruleset.max_increment_for_match]
        self.timer = Timer(ruleset.turn_duration, self.next_turn)
        self.status: Literal["ready", "running", "waiting", "ended"] = "ready"
        self.video_consumer = VideoConsumer(self.start_movement, self.stop_movement)

    def start_movement(self):
        if self.status == "running":
            self.status = "waiting"
            self.timer.pause()

    def stop_movement(self):
        if self.status == "waiting":
            self.status = "running"
            self.next_turn()

    def start_game(self):
        """Avvia il gioco e inizia il turno per il primo giocatore."""
        if self.status == "ready":
            self.status = "running"
            self.start_turn()

    def end_game(self):
        """Ferma il gioco e cancella tutti i timer."""
        if self.status != "ended":
            self.timer.end()
            self.video_consumer.end()
            self.status = "ended"
            #TODO: Controllare bene se tutto è stato terminato
            print("Gioco terminato.")

    """------TURN COMMANDS-----"""

    def increment_time(self):
        if self.status == "running":
            if self.remaining_increments[self.current_player] > 0:
                self.remaining_increments[self.current_player] -= 1
                # TODO: valutare se mettere in pausa il timer per l'incremento oppure no
                self.timer.add_time(self.ruleset.increment_duration)
            else:
                print(f"Nessun incremento disponibile per il giocatore: {self.player_names[self.current_player]}")

    def remaining_increments(self, player=None):
        if player is None:
            player = self.current_player
        return self.remaining_increments[player]

    def next_turn(self):
        if self.status == "running":
            self.current_player = self.current_player + 1 % 2
            # TODO: Forse necessario un controllo per verificare che il thread del timer si è chiuso
            self.timer = Timer(self.ruleset.turn_duration,
                               self.next_turn)  # Qui ricreo il timer, TODO: da testare se effettivamente si chiude bene il vecchio thread del timer
            self.start_turn()

    def start_turn(self):
        """Inizia il turno per il giocatore corrente e avvia il timer."""
        self.timer.start()

    def pause_turn(self):
        """
        Mette in pausa il timer del turno, NON LO TERMINA.
        Per terminare il timer e passare al successivo utilizzare la funzione end_turn()
        """
        self.timer.pause()

    def resume_turn(self):
        """
        Riprende l'esecuzione del timer, funziona solo se il timer è in pausa, non fa nulla se non lo è
        """
        self.timer.resume()

    def end_turn(self):
        """Termina il turno corrente e passa al giocatore successivo."""
        # TODO: Si potrebbe aggiungere del tempo di attesa (10-15 secondi) prima di inizare il turno
        self.timer.end()
        self.next_turn()
