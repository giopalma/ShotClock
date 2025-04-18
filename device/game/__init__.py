import threading
import time
from typing import Literal
import logging
from gpiozero import Buzzer
import os

from .video_consumer import VideoConsumer
from device.game.ruleset import Ruleset
from device.game.timer import Timer
from device.table import TablePreset
from device.utils import is_raspberry_pi
from device.video_producer import VideoProducer


class Game:
    """
    Gestisce la logica di un gioco a turni per due giocatori basato su un set di regole e una configurazione del tavolo.

    Caratteristiche:
    - Stato del gioco: "ready", "running", "waiting", "ended", "paused".
    - Coordinamento dei turni mediante un timer.
    - Gestione degli eventi di movimento tramite un video consumer.
    - Possibilità di incrementare il tempo disponibile per il turno.

    Attributi:
    _ruleset (Ruleset): Set di regole con parametri quali durata del turno e incrementi massimi.
    _table (TablePreset): Configurazione del tavolo di gioco.
    player_names (List[str]): Nomi dei due giocatori.
    increments (List[int]): Numero di incrementi disponibili per ciascun giocatore.
    _timer (Timer): Timer che gestisce la durata di ogni turno.
    status (Literal["ready", "running", "waiting", "ended", "paused"]): Stato attuale del gioco.
    _video_consumer (VideoConsumer): Gestore degli eventi video per il movimento.
    last_remaining_time (int): Ultimo tempo rimanente registrato.
    socketio: Oggetto per la comunicazione via WebSocket.
    """

    def __init__(
        self,
        ruleset: Ruleset,
        table: TablePreset,
        player1_name: str,
        player2_name: str,
        video_producer: VideoProducer,
        socketio=None,
    ):
        """
        Inizializza una nuova istanza di Game impostando il set di regole, la configurazione del tavolo e i nomi dei giocatori.

        Parametri:
            ruleset (Ruleset): Set di regole che definisce i parametri di gioco (es. durata del turno, incrementi massimi).
            table (TablePreset): Configurazione del tavolo su cui si svolge il gioco.
            player1_name (str): Nome del primo giocatore.
            player2_name (str): Nome del secondo giocatore.
            video_producer (VideoProducer): Oggetto che gestisce la produzione di video (Opzionale). Permette maggiore facilità di testing
            socketio (SocketIO): Oggetto per la comunicazione via WebSocket.
        """
        self.ruleset = ruleset
        self.table = table

        self._is_running_rpi = is_raspberry_pi()
        self._buzzer = Buzzer(11) if self._is_running_rpi else None
        self.player_names = [player1_name, player2_name]
        self.increments = [
            ruleset.max_increment_for_match,
            ruleset.max_increment_for_match,
        ]
        self._timer = self._new_timer(ruleset.initial_duration)
        self.status: Literal["ready", "running", "waiting", "ended", "paused"] = "ready"
        self._video_consumer = VideoConsumer(
            table=table,
            video_producer=video_producer,
            start_movement_callback=self._start_movement,
            stop_movement_callback=self._stop_movement,
        )
        self.last_remaining_time = 0
        self.socketio = socketio

    def _emit_websocket(self, event, body):
        if os.getenv("FLASK_ENV") == "api":
            self.socketio.emit(event, body)

    def start(self):
        """Avvia il gioco e inizia il turno per il primo giocatore."""
        if self.status == "ready":
            self.status = "running"
            self._video_consumer.start()
            self.start_turn()
            self._emit_websocket("game", "started")
        else:
            return "Game already started."

    def end(self):
        """Ferma il gioco e cancella tutti i timer."""
        if self.status != "ended":
            self.resume()  # Importante se viene chiuso mentre è in pausa
            self._timer.end()
            self._video_consumer.end()
            self.status = "ended"
            self._emit_websocket("game", "ended")
            if self._buzzer:
                self._buzzer.off()
                self._buzzer.close()
            print("Gioco terminato.")

    """------MOVEMENT EVENTS CALLBACKS-----"""

    def _start_movement(self):
        if self.status == "running":
            self.status = "waiting"
            remaining_time = self._timer.pause()
            if os.getenv("FLASK_ENV") == "api":
                self.socketio.emit(
                    "timer",
                    {
                        "timestamp": time.time(),
                        "remaining_time": remaining_time,
                        "status": "paused",
                    },
                )

    def _stop_movement(self):
        if self.status == "waiting":
            self.status = "running"
            self.next_turn()

    """------TURN COMMANDS-----"""

    def increment_time(self, player):
        if self.status == "running":
            if self.increments[player] > 0:
                self.increments[player] -= 1
                self._timer.add_time(self.ruleset.increment_duration)
            else:
                return f"Nessun incremento disponibile per il giocatore: {self.player_names[player]}"

    def next_turn(self):
        if self.status == "running":
            self._timer.end()
            self._timer = self._new_timer(duration=self.ruleset.turn_duration)
            self.start_turn()

    def start_turn(self):
        """Inizia il turno per il giocatore corrente e avvia il timer."""
        self._timer.start()

    def pause(self):
        """
        Mette in pausa il timer del turno, NON LO TERMINA.
        Per terminare il timer e passare al successivo utilizzare la funzione end_turn()
        """
        if self.status == "running":
            remaining_time = self._timer.pause()
            self._video_consumer.pause()
            if os.getenv("FLASK_ENV") == "api":
                self.socketio.emit(
                    "timer",
                    {
                        "timestamp": time.time(),
                        "remaining_time": remaining_time,
                        "status": "paused",
                    },
                )
            self.status = "paused"

    def resume(self):
        """
        Riprende l'esecuzione del timer, funziona solo se il timer è in pausa, non fa nulla se non lo è
        """
        if self.status == "paused":
            remaining_time = self._timer.resume()
            self._video_consumer.resume()
            if os.getenv("FLASK_ENV") == "api":
                self.socketio.emit(
                    "timer",
                    {
                        "timestamp": time.time(),
                        "remaining_time": remaining_time,
                        "status": "running",
                    },
                )
            self.status = "running"

    def end_turn(self):
        """Termina il turno corrente e passa al giocatore successivo."""
        self._timer.end()
        self.next_turn()

    """------BUZZER / SUONO-----"""
    TIME_SOUND_BUZZER = 0.5
    TIME_FINAL_BUZZER = 2.0  # Durata del suono finale (2 secondi)

    def _buzzer(self, duration=TIME_SOUND_BUZZER):
        if duration:
            self._buzzer.beep(on_time=duration, off_time=duration, n=1)

    def _allarm(self, is_final=False):
        duration = self.TIME_FINAL_BUZZER if is_final else self.TIME_SOUND_BUZZER

        if self._is_running_rpi:
            t = threading.Thread(target=self._buzzer, args=(duration))
            t.start()
        else:
            # Quando viene eseguito su Windows
            import winsound

            winsound.Beep(1000, int(1000 * duration))

    """------ TIMER -----"""

    def _new_timer(self, duration: int):
        return Timer(
            duration=duration,
            allarm_time=self.ruleset.allarm_time,
            callback=self._time_up,
            allarm_callback=self._allarm,
            periodic_callback=self._periodic_callback,
            periodic_time=1,
        )

    def _time_up(self):
        # Metodo chiamato quando il timer raggiunge 0
        self._allarm(is_final=True)
        self.next_turn()

    def _periodic_callback(self, remaining_time, is_timer_running):
        self.last_remaining_time = remaining_time
        if os.getenv("FLASK_ENV") == "api":
            self.socketio.emit(
                "timer",
                {
                    "timestamp": time.time(),
                    "remaining_time": remaining_time,
                    "status": "running" if is_timer_running else "paused",
                },
            )

        logging.info(f"Remaining time: {remaining_time}")
