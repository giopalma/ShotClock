import time
from threading import Thread, Event


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
        self._stop_event = Event()
        self._pause_event = Event()
        self.thread = None

    def _run(self):
        """Esegue il conto alla rovescia del timer."""
        start_time = time.time()
        while not self._stop_event.is_set() and self.remaining_time > 0:
            if self._pause_event.is_set():
                start_time = time.time()  # Reset per calcolare la pausa
                self._pause_event.wait()  # Aspetta che la pausa termini
            elapsed = time.time() - start_time
            self.remaining_time = max(0, self.duration - elapsed)
            time.sleep(0.1)  # Controllo frequente per fluidità

        if self.remaining_time == 0 and not self._stop_event.is_set():
            self.callback()

    def start(self):
        """Avvia il timer."""
        self._stop_event.clear()
        self._pause_event.clear()
        self.thread = Thread(target=self._run, daemon=True)
        self.thread.start()

    def pause(self):
        """Metti in pausa il timer."""
        self._pause_event.set()

    def resume(self):
        """Riprendi il timer dalla pausa."""
        self._pause_event.clear()
        self._pause_event.set()  # Forza un segnale per uscire dalla pausa

    def stop(self):
        """Ferma il timer."""
        self._stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join()
