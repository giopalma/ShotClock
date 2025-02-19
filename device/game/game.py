from typing import Literal

from .ruleset import Ruleset
from .timer import Timer


class Game:
    def __init__(self, ruleset: Ruleset, player1_name: str, player2_name):
        self.ruleset = ruleset
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.current_player = 1
        self.timer = Timer(ruleset.turn_duration, self.next_turn)
        self.status: Literal["ready", "running", "waiting", "ended"] = "ready"

    def start_game(self):
        """Avvia il gioco e inizia il turno per il primo giocatore."""
        if self.status == "ready":
            self.status = "running"
            self.start_turn()

    def end_game(self):
        """Ferma il gioco e cancella tutti i timer."""
        if self.status != "ended":
            self.end_timer()
            print("Gioco terminato.")

    def next_turn(self):
        if self.status == "running":
            self.current_player = self.current_player + 1 % 2
            # TODO: Forse necessario un controllo per verificare che il thread del timer si è chiuso
            self.timer = Timer(self.ruleset.turn_duration, self.next_turn) # Qui ricreo il timer, TODO: da testare se effettivamente si chiude bene il vecchio thread del timer
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