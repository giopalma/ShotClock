from dataclasses import dataclass


@dataclass
class Ruleset:
    """
    Classe Ruleset che rappresenta un insieme di regole per il gioco del biliardo.
    Attributi:
        id (int): Identificativo univoco del set di regole.
        name (str): Nome del set di regole.
        initial_duration (int): Durata iniziale del gioco in secondi.
        turn_duration (int): Durata di ogni turno in secondi.
        allarm_time (int): A quanto tempo dalla fine del turno deve essere attivato l'allarme in secondi.
        increment_duration (int): Incremento di tempo per ogni turno in secondi.
        max_increment_for_match (int): Incremento massimo totale per la partita in secondi.
    """

    id: int
    name: str
    initial_duration: int
    turn_duration: int
    allarm_time: int
    increment_duration: int
    max_increment_for_match: int
