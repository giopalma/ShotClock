from .ruleset import Ruleset
from . import Game


_game = None


def get_game() -> Game:
    """
    Restituisce il gioco attualmente in esecuzione.
    Se non c'è alcun gioco in esecuzione, restituisce None.
    """
    return _game


def new_game(ruleset: Ruleset, player1_name: str, player2_name) -> Game:
    """
    Crea un nuovo gioco con le regole specificate e i nomi dei giocatori.
    Se esiste già un gioco in corso, lo termina e ne crea uno nuovo.
    """
    if _game is not None:
        _game.end()
    _game = Game(ruleset, player1_name, player2_name)
    return _game
