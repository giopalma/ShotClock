import time
from threading import Thread, Event
import logging
from math import floor


# TODO: Ricontrollare il timer
class Timer:
    def __init__(self, duration: int, allarm_time: int, callback, allarm_callback):
        """
        Inizializza un timer.
        :param duration: Durata del timer in secondi.
        :param callback: Funzione da chiamare quando il timer scade.
        """
        self.duration = duration
        self.remaining_time = duration
        self.callback = callback

        self.allarm_time = allarm_time
        self.allarm_callback = allarm_callback
        self._allarm_triggered = False

        self._pause_event = Event()
        self._end_event = (
            Event()
        )  # L'end event è necessario per terminare il loop del run
        # TODO: Qui già si potrebbe creare il thread se si mette subito il _pause_event a True, tanto c'è il blocco del while
        self.thread = None

    def _run(self):
        """
        Esegue il conto alla rovescia del timer. Se il timer è scaduto oppure viene formato il termine del timer,
        allora viene eseguita la funzione di callback.
        """
        while (not self._end_event.is_set()) and (self.remaining_time > 0):
            if not self._pause_event.is_set():
                debug_last_remaining_time = floor(self.remaining_time)
                start_time = time.time()
                time.sleep(0.01)  # TODO: Impostare la precisione tramite config
                elapsed = time.time() - start_time
                self.remaining_time = max(0, self.remaining_time - elapsed)
                if (
                    self.remaining_time <= self.allarm_time
                    and not self._allarm_triggered
                ):
                    # self.allarm_callback()
                    self._allarm_triggered = True
                elif self.remaining_time <= 0:
                    self.callback()
                # DEBUG
                if floor(self.remaining_time) != debug_last_remaining_time:
                    logging.info(
                        f"Timer: {floor(self.remaining_time)} remaining time",
                    )

    def start(self):
        """Avvia il timer."""
        self._pause_event.clear()
        self.thread = Thread(target=self._run, daemon=True)
        self.thread.name = "TimerThread"
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
