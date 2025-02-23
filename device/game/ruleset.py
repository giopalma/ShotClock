from dataclasses import dataclass


@dataclass
class Ruleset:
    """
    Classe che rappresenta le regole del timer di gioco.
    L'utente può creare e modificare i ruleset per personalizzare il gioco.
    Quando deve creare un nuovo gioco, deve selezionare il ruleset da utilizzare.
    """

    id: int
    name: str
    initial_duration: int
    turn_duration: int
    allarm_time: int
    increment_duration: int
    max_increment_for_match: int
