import json


class Preset:
    """
    L'oggetto Preset contiene le informazioni che l'utente ha inserito durante la configurazione del dispositivo. Durante la fase di setup del dispositivo, l'utente crea un Preset per il tavolo da gioco e la posizione del dispositivo. Il Preset può essere scelto tramite l'utilizzo della piaattaforma Web.
    Il preset tutte le informazioni necessarie per il setup.
    """

    def __init__(self, points, colors):
        """_summary_

        Args:
            points (Array of Tuple of Int): Array di 4 tuple di interi che rappresentano le coordinate dei punti di calibrazione del tavolo da gioco. Le coordinate sono in formato (x, y).
            colors (Array of string): Array di stringhe che rappresentano i colori in formato esadecimale. Ad esempio: #FF0000 per il rosso.
        """
        self.points = points
        self.colors = colors

    def serialize(self) -> str:
        """
        Serializza l'oggetto Preset in una stringa JSON.

        Returns:
            str: Stringa JSON che rappresenta l'oggetto Preset.
        """
        return json.dumps(self.__dict__, indent=4)

    # TODO: Implementazione della classe Preset con le proprietà necessarie


def deserialize(json_data: str) -> Preset:
    """
    Deserializza una stringa JSON in un oggetto Preset.

    Args:
        json (str): Stringa JSON che rappresenta l'oggetto Preset.


    Returns:
        Preset: Oggetto Preset deserializzato dalla stringa JSON. Restituisce None se la stringa JSON non è valida oppure non è stato possibile deserializzare l'oggetto Preset.

    """
    return Preset(**json.loads(json_data))


def get_default_preset() -> Preset:
    """
    Recupera il preset di default. Il preset di default è il preset che viene utilizzato quando il dispositivo viene avviato senza aver selezionato un preset specifico.
    Returns:
        Preset: Preset impostato di default. Restituisce None se il preset non è stato trovato oppure non è valido.
    """
    # TODO: Implementazione della funzione di recupero del preset di default

    return None
