"""
Il modulo `game_manager` fornisce i metodi essenziali per la gestione base del gioco di biliardo.
Il suo scopo è limitato a ottenere il riferimento al gioco corrente, creare un nuovo gioco o terminare quello esistente.

Classi:
    Nessuna
Funzioni:
    get_game() -> Game:
    new_game(ruleset: Ruleset, player1_name: str, player2_name: str) -> Game:
    end_game() -> None:
Variabili:
    _game: Game
        Variabile globale che mantiene il riferimento al gioco attualmente in esecuzione.
"""

from .ruleset import Ruleset
from . import Game
from device.table import TablePreset
from device.video_producer import VideoProducer

_game: Game | None = None


def get_game() -> Game:
    """
    Restituisce il gioco attualmente in esecuzione.
    Se non c'è alcun gioco in esecuzione, restituisce None.
    """
    return _game


def new_game(
    ruleset: Ruleset, table: TablePreset, player1_name: str, player2_name, socketio
) -> Game:
    """
    Crea un nuovo gioco con le regole specificate e i nomi dei giocatori.
    Se esiste già un gioco in corso, lo termina e ne crea uno nuovo.
    """
    global _game
    if _game is not None:
        _game.end()
    _game = Game(
        ruleset=ruleset,
        table=table,
        player1_name=player1_name,
        player2_name=player2_name,
        video_producer=VideoProducer.get_instance(),
        socketio=socketio,
    )
    socketio.emit("game", "created")
    return _game


def end_game():
    """
    Termina il gioco attualmente in esecuzione.
    """
    global _game
    if _game is not None:
        _game.end()
        _game = None
    else:
        return "No game in progress"
