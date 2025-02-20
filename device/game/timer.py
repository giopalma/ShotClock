import time
from threading import Thread, Event


# TODO: Ricontrollare il timer
class Timer:
    def __init__(self, duration, callback):
        """
        Inizializza un timer.
        :param duration: Durata del timer in secondi.
        :param callback: Funzione da chiamare quando il timer scade.
        """
        self.duration = duration
        self.callback = callback
        self.remaining_time = duration
        self._pause_event = Event()
        self._end_event = Event() # L'end event è necessario per terminare il loop del run
        # TODO: Qui già si potrebbe creare il thread se si mette subito il _pause_event a True, tanto c'è il blocco del while
        self.thread = None

    def _run(self):
        """
        Esegue il conto alla rovescia del timer. Se il timer è scaduto oppure viene formato il termine del timer,
        allora viene eseguita la funzione di callback.
        """
        while not self._end_event.is_set() and self.remaining_time > 0:
            if not self._pause_event.is_set():
                start_time = time.time()
                time.sleep(0.1) # TODO: Impostare la precisione tramite config
                elapsed = time.time() - start_time
                self.remaining_time = max(0, self.remaining_time - elapsed)
        self.callback()

    def start(self):
        """Avvia il timer."""
        self._pause_event.clear()
        self.thread = Thread(target=self._run, daemon=True)
        self.thread.start()

    def pause(self):
        """Metti in pausa il timer."""
        self._pause_event.set()

    def resume(self):
        """Riprendi il timer dalla pausa."""
        self._pause_event.clear()

    def end(self):
        """
        Ferma il timer.
        Viene mandato l'evento end_event e viene terminato il thread.
        """
        if self.thread and self.thread.is_alive():
            self._end_event.set()
            self.thread.join()
