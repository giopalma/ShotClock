import threading
import time
from typing import Literal

from .video_consumer import VideoConsumer
from device.game.ruleset import Ruleset
from device.game.timer import Timer
from device.table import TablePreset
from device.utils import is_raspberry_pi
import logging
from gpiozero import Buzzer
import winsound


class Game:
    """
    Gestisce la logica di un gioco a turni per due giocatori basato su un set di regole e una configurazione del tavolo.

    Caratteristiche:
    - Stato del gioco: "ready", "running", "waiting", "ended".
    - Coordinamento dei turni mediante un timer.
    - Gestione degli eventi di movimento tramite un video consumer.
    - Possibilità di incrementare il tempo disponibile per il turno.

    Attributi:
    ruleset (Ruleset): Set di regole con parametri quali durata del turno e incrementi massimi.
    table (TablePreset): Configurazione del tavolo di gioco.
    player_names (List[str]): Nomi dei due giocatori.
    current_player (int): Indice del giocatore corrente (0 o 1).
    increments (List[int]): Numero di incrementi disponibili per ciascun giocatore.
    timer (Timer): Timer che gestisce la durata di ogni turno.
    status (Literal["ready", "running", "waiting", "ended"]): Stato attuale del gioco.
    video_consumer (VideoConsumer): Gestore degli eventi video per il movimento.
    """

    def __init__(
        self,
        ruleset: Ruleset,
        table: TablePreset,
        player1_name: str,
        player2_name: str,
        video_producer,
    ):
        """
        Inizializza una nuova istanza di Game impostando il set di regole, la configurazione del tavolo e i nomi dei giocatori.

        Parametri:
            ruleset (Ruleset): Set di regole che definisce i parametri di gioco (es. durata del turno, incrementi massimi).
            table (TablePreset): Configurazione del tavolo su cui si svolge il gioco.
            player1_name (str): Nome del primo giocatore.
            player2_name (str): Nome del secondo giocatore.
            video_producer (VideoProducer): Oggetto che gestisce la produzione di video (Opzionale). Permette maggiore facilità di testing
        """
        self._ruleset = ruleset
        self._table = table

        self._is_running_rpi = is_raspberry_pi()
        self._buzzer = Buzzer(11) if self._is_running_rpi else None
        self._player_names = [player1_name, player2_name]
        self._current_player = 1
        self._increments = [
            ruleset.max_increment_for_match,
            ruleset.max_increment_for_match,
        ]
        self._timer = Timer(
            duration=ruleset.initial_duration,
            allarm_time=ruleset.allarm_time,
            callback=self.next_turn,
            allarm_callback=self._allarm,
        )
        self._status: Literal["ready", "running", "waiting", "ended"] = "ready"
        self._video_consumer = VideoConsumer(
            table=table,
            video_producer=video_producer,
            start_movement_callback=self._start_movement,
            stop_movement_callback=self._stop_movement,
        )

    def start(self):
        """Avvia il gioco e inizia il turno per il primo giocatore."""
        if self._status == "ready":
            self._status = "running"
            self._video_consumer.start()
            self.start_turn()

    def end(self):
        """Ferma il gioco e cancella tutti i timer."""
        if self._status != "ended":
            self._timer.end()
            self._video_consumer.end()
            self._status = "ended"
            # TODO: Controllare bene se tutto è stato terminato
            print("Gioco terminato.")

    """------MOVEMENT EVENTS CALLBACKS-----"""

    def _start_movement(self):
        if self._status == "running":
            self._status = "waiting"
            self._timer.pause()

    def _stop_movement(self):
        if self._status == "waiting":
            self._status = "running"
            self.next_turn()

    """------TURN COMMANDS-----"""

    def increment_time(self):
        if self._status == "running":
            if self._increments[self._current_player] > 0:
                self._increments[self._current_player] -= 1
                # TODO: valutare se mettere in pausa il timer per l'incremento oppure no
                self._timer.add_time(self._ruleset.increment_duration)
            else:
                print(
                    f"Nessun incremento disponibile per il giocatore: {self._player_names[self._current_player]}"
                )

    def remaining_increments(self, player=None):
        if player is None:
            player = self._current_player
        return self._increments[player]

    def next_turn(self):
        if self._status == "running":
            self._current_player = self._current_player + 1 % 2
            self._timer.end()  # Termino il vecchio timer
            self._timer = Timer(
                duration=self._ruleset.turn_duration,
                allarm_time=self._ruleset.allarm_time,
                callback=self.next_turn,
                allarm_callback=self._allarm,
            )  # Qui ricreo il timer, TODO: da testare se effettivamente si chiude bene il vecchio thread del timer
            self.start_turn()

    def start_turn(self):
        """Inizia il turno per il giocatore corrente e avvia il timer."""
        self._timer.start()

    def pause_turn(self):
        """
        Mette in pausa il timer del turno, NON LO TERMINA.
        Per terminare il timer e passare al successivo utilizzare la funzione end_turn()
        """
        self._timer.pause()

    def resume_turn(self):
        """
        Riprende l'esecuzione del timer, funziona solo se il timer è in pausa, non fa nulla se non lo è
        """
        self._timer.resume()

    def end_turn(self):
        """Termina il turno corrente e passa al giocatore successivo."""
        # TODO: Si potrebbe aggiungere del tempo di attesa (10-15 secondi) prima di inizare il turno
        self._timer.end()
        self.next_turn()

    TIME_SOUND_BUZZER = 1

    def _buzzer(self):
        self._buzzer.on()
        time.sleep(self.TIME_SOUND_BUZZER)
        self._buzzer.off()

    def _allarm(self):
        if self._is_running_rpi:
            t = threading.Thread(target=self._buzzer)
            t.start()
        else:
            # Quando viene eseguito su Windows
            winsound.Beep(1000, int(1000 * self.TIME_SOUND_BUZZER))
