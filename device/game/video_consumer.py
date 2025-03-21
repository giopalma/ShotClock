from threading import Event, Thread
import time
import cv2
import numpy as np
import logging
from device.video_producer import VideoProducer
from device.table import TablePreset
from device.utils import CircularArray


class VideoConsumer:
    """
    VideoConsumer riconosce il movimento delle biglie da gioco.
    Viene eseguito in un thread separato e utilizza un meccanismo di debounce e hysteresis temporale
    per evitare falsi positivi dovuti a variazioni troppo rapide.
    """

    NUMBER_OF_MOTION_COUNT = 10
    CURRENT_MOTION_THRESHOLD = 100  # Soglia per considerare che vi sia movimento
    CIRCULARITY_THRESHOLD = 0.7  # Soglia per filtrare contorni non circolari
    H_DIFF, S_DIFF, V_DIFF = 5, 10, 5  # Differenze per il filtro colore in HSV
    MIN_AREA_THRESHOLD = 200
    # Tempo minimo (in secondi) tra cambi di stato
    MIN_STATE_CHANGE_INTERVAL = 0.5

    def __init__(
        self,
        table: TablePreset,
        start_movement_callback,
        stop_movement_callback,
        video_producer: VideoProducer,
    ):
        """
        Inizializza il VideoConsumer.

        Args:
            table (TablePreset): Preset del tavolo contenente punti e colori.
            start_movement_callback (callable): Funzione chiamata al rilevamento del movimento.
            stop_movement_callback (callable): Funzione chiamata al passaggio allo stato fermo.
            video_producer (VideoProducer): Istanza del produttore video.
        """
        self.table = table
        self.start_movement_callback = start_movement_callback
        self.stop_movement_callback = stop_movement_callback
        self._video_producer = video_producer

        self._is_running = Event()
        self._is_running.clear()
        self._end_event = Event()

        self._thread = Thread(target=self.run, name="VideoConsumerThread")
        self._thread.daemon = False  # Non è daemon per garantire una chiusura ordinata
        self._thread.start()

        self._last_state_change_time = 0  # Tempo dell'ultimo cambio di stato
        self._prev_frame_time = 0
        self._current_fps = 0

    def start(self):
        """Avvia il ciclo di elaborazione del video."""
        self._is_running.set()

    def pause(self):
        """Pausa il ciclo di elaborazione e resetta le cronologie."""
        self._is_running.clear()

    def resume(self):
        """Riprende il ciclo di elaborazione dopo una pausa."""
        self.start()

    def end(self):
        """Termina il ciclo di elaborazione se il thread è attivo."""
        if self._thread and self._thread.is_alive():
            self._end_event.set()

    def run(self):
        """
        Ciclo principale del VideoConsumer.
        - Acquisisce il frame, applica i filtri e aggiorna il buffer dei frame.
        - Calcola il movimento tramite confronto tra 3 frame.
        - Utilizza un buffer per il debounce e applica una finestra temporale minima per evitare
          cambiamenti troppo rapidi tra movimento e fermo.
        """
        balls_mask_history = CircularArray(3)
        motion_history = CircularArray(self.NUMBER_OF_MOTION_COUNT)
        isMoving = False

        while self._video_producer.is_opened() and not self._end_event.is_set():
            time.sleep(0.05)

            if not self._is_running.is_set():
                balls_mask_history = CircularArray(3)
                motion_history = CircularArray(self.NUMBER_OF_MOTION_COUNT)
                continue

            self._last_state_change_time = time.time()
            blurred = self._video_producer.get_frame_blurred()
            cv2.imshow("Blurred", blurred)
            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
            current_balls_mask = self._create_mask(
                hsv, self.table.points, self.table.colors
            )
            balls_mask_history.add(current_balls_mask)

            if balls_mask_history.get_len() == 3:
                current_motion = self._motion_count(balls_mask_history.get_array())
                motion_history.add(current_motion)

                # Visualizza il risultato corrente sul frame

                # Controlla se un tasto è premuto
                key = cv2.waitKey(1)
                if key == ord("p"):  # Usa il tasto 'p' per bloccare le schermate
                    while cv2.waitKey(1) != ord("p"):
                        pass  # Attendi fino a quando il tasto 'p' viene premuto di nuovo

                if motion_history.get_len() == self.NUMBER_OF_MOTION_COUNT:
                    history = motion_history.get_array()
                    motion_count = sum(history)
                    if motion_count > self.NUMBER_OF_MOTION_COUNT * 0.7:
                        new_motion_state = True
                    else:
                        new_motion_state = False
                    if new_motion_state != isMoving:
                        isMoving = new_motion_state
                        if new_motion_state:
                            logging.info("Movimento rilevato")
                            self.start_movement_callback()
                        else:
                            logging.info("Movimento terminato")
                            self.stop_movement_callback()

                    test_image = blurred.copy()
                    text = "MOVIMENTO" if isMoving else "FERMO"
                    cv2.putText(
                        test_image,
                        text,
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 255, 255),
                        2,
                        cv2.LINE_AA,
                    )
                    cv2.imshow("Blurred with movement", test_image)

    def _motion_count(self, balls_mask_history):
        """
        Determina se c'è stato movimento tra i frame delle biglie rilevate.

        Args:
            balls_mask_history (list): Array contenente le maschere delle biglie degli ultimi 3 frame.

        Returns:
            bool: True se è stato rilevato movimento, False altrimenti.
        """
        frame_p2 = balls_mask_history[0]  # Frame -2
        frame_p1 = balls_mask_history[1]  # Frame -1
        frame_c = balls_mask_history[2]  # Frame corrente

        # Converti i frame in immagini binarie
        _, frame_p2 = cv2.threshold(frame_p2, 127, 255, cv2.THRESH_BINARY)
        _, frame_p1 = cv2.threshold(frame_p1, 127, 255, cv2.THRESH_BINARY)
        _, frame_c = cv2.threshold(frame_c, 127, 255, cv2.THRESH_BINARY)

        # Calcola le differenze assolute tra frame consecutivi
        diff1 = cv2.absdiff(frame_p1, frame_p2)
        diff2 = cv2.absdiff(frame_c, frame_p1)

        # Rimuovi piccoli artefatti con operazioni morfologiche
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        diff1 = cv2.morphologyEx(diff1, cv2.MORPH_OPEN, kernel)
        diff2 = cv2.morphologyEx(diff2, cv2.MORPH_OPEN, kernel)

        white_pixel_frame_d1 = cv2.countNonZero(diff1)
        white_pixel_frame_d2 = cv2.countNonZero(diff2)
        max_white_pixel = max(white_pixel_frame_d1, white_pixel_frame_d2)

        # Visualizza i frame differenza per debugging
        cv2.imshow("Diff1", diff1)
        cv2.imshow("Diff2", diff2)

        return max_white_pixel > self.CURRENT_MOTION_THRESHOLD

    def _create_mask(self, hsv, points, colors):
        """
        Crea una maschera per rilevare le biglie da gioco basata sui colori e sulla forma del tavolo.

        Args:
            hsv (Mat): Frame in formato HSV.
            points (list of tuple): Punti (x,y) che definiscono il poligono del tavolo.
            colors (list of tuple): Lista di colori in formato HSV per il tavolo.

        Returns:
            Mat: Maschera binaria contenente i contorni delle biglie.
        """
        # Definisce l'intervallo di colore basato sui valori minimi e massimi dei colori
        color_lower = tuple(
            min(color[i] for color in colors) - diff
            for i, diff in enumerate([self.H_DIFF, self.S_DIFF, self.V_DIFF])
        )
        color_upper = tuple(
            max(color[i] for color in colors) + diff
            for i, diff in enumerate([self.H_DIFF, self.S_DIFF, self.V_DIFF])
        )

        # Crea una maschera rettangolare basata sui punti del tavolo
        points = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
        rec_mask = cv2.fillPoly(np.zeros(hsv.shape[:2], dtype=np.uint8), [points], 255)

        # Crea la maschera di colore e la inverte
        color_mask = cv2.inRange(hsv, color_lower, color_upper)
        color_mask = cv2.dilate(color_mask, None, iterations=2)
        color_mask = cv2.bitwise_not(color_mask)

        # Combina la maschera di colore con quella del tavolo
        combined_mask = cv2.bitwise_and(color_mask, rec_mask)

        # Trova i contorni e filtra per circolarità
        contours, _ = cv2.findContours(
            combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        circularity_mask = np.zeros_like(combined_mask)
        for c in contours:
            area = cv2.contourArea(c)
            # Controllo sulla dimensione dell'area del contorno
            if area < self.table.min_area_threshold:
                continue
            perimeter = cv2.arcLength(c, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * area / (perimeter**2)
            if circularity > self.CIRCULARITY_THRESHOLD:
                cv2.drawContours(circularity_mask, [c], -1, 255, thickness=cv2.FILLED)

        # Visualizza le maschere intermedie per debugging
        cv2.imshow("Combined Mask", combined_mask)
        cv2.imshow("Circularity Mask", circularity_mask)
        return circularity_mask
