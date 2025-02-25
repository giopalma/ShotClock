import time
from threading import Lock, Thread, Event


class Timer:
    def __init__(
        self,
        duration: int,
        allarm_time: int,
        callback,
        allarm_callback,
        periodic_callback,
        periodic_time=1,
    ):
        """
        Inizializza un timer.
        :param duration: Durata del timer in secondi.
        :param callback: Funzione da chiamare quando il timer scade.
        """
        self.duration = duration
        self.remaining_time = duration
        self._remaining_time_lock = Lock()
        self.callback = callback
        self.allarm_time = allarm_time
        self.allarm_callback = allarm_callback
        self.periodic_callback = periodic_callback
        self.periodic_time = periodic_time
        self._allarm_triggered = False
        self._is_running_event = Event()
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
        _last_time_check = time.monotonic()
        while (not self._end_event.is_set()) and (self.remaining_time > 0):
            start_time = time.monotonic()
            if not self._is_running_event.is_set():
                self._is_running_event.wait()  # Attende che il timer venga ripreso
                start_time = time.monotonic()

            time.sleep(max(0.001, min(self.remaining_time / 10, 0.1)))

            elapsed = time.monotonic() - start_time
            with self._remaining_time_lock:
                self.remaining_time = max(0, self.remaining_time - elapsed)

            current_time = time.monotonic()
            if current_time - _last_time_check >= self.periodic_time:
                self.periodic_callback(self.remaining_time)
                _last_time_check = current_time

            if self.remaining_time <= self.allarm_time and not self._allarm_triggered:
                self.allarm_callback()
                self._allarm_triggered = True
            elif self.remaining_time <= 0:
                self.callback()

    def start(self):
        """Avvia il timer."""
        self._is_running_event.set()
        self.thread = Thread(target=self._run, daemon=True)
        self.thread.name = "TimerThread"
        self.thread.start()

    def pause(self):
        """Metti in pausa il timer."""
        self._is_running_event.clear()

    def resume(self):
        """Riprendi il timer dalla pausa."""
        self._is_running_event.set()

    def end(self):
        """
        Ferma il timer.
        Viene mandato l'evento end_event e viene terminato il thread.
        """
        if self.thread and self.thread.is_alive():
            self._end_event.set()
