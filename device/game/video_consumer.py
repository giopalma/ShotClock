from threading import Event, Thread
import time
from device.video_producer import VideoProducer
from device.table import TablePreset
import cv2
import numpy as np

# import imutils
from device.utils import CircularArray


class VideoConsumer:
    """
    VideoConsumer è la classe che effettivamente riconosce il movimento delle biglie da gioco.
    Viene eseguito dal Game ed esegue nel suo stesso thread dato che l'unico loop che viene
    eseguito in questo thread (il timer viene eseguito in un thread separato).
    """

    def __init__(
        self,
        table: TablePreset,
        start_movement_callback,
        stop_movement_callback,
        video_producer: VideoProducer,  # Il video producer, nonostate sia un singleton glielo passo come parametro per rendere il codice più testabile
    ):
        self._video_producer = video_producer
        self._thread = Thread(target=self.run)
        self._thread.daemon = False  # Il thread del video consumer è un thread demon, quindi non blocca l'uscita del programma
        self._thread.name = "VideoConsumerThread"
        """
        Queste due fuzioni sono dei callback che vengono chiamati quando il VideoConsumer cambia di stato
        MOVIMENTO -> FERMO : stop_movement_callback
        FERMO -> MOVIMENTO : start_movement_callback
        """
        self.start_movement_callback = start_movement_callback
        self.stop_movement_callback = stop_movement_callback
        self.table = table
        self._is_running = Event()
        self._is_running.clear()
        self._end_event = Event()
        self._thread.start()

    def start(self):
        self._is_running.set()

    def end(self):
        if self._thread and self._thread.is_alive():
            self._end_event.set()

    def pause(self):
        self._is_running.clear()

    NUMBER_OF_MOTION_COUNT = 3

    def run(self):
        """
        Esegue il ciclo principale del video consumer.
        Il metodo continua a eseguire il ciclo finché il video producer è aperto.
        Durante ogni iterazione del ciclo:
        - Attende che il segnale `_is_running` sia impostato.
        - Ottiene un frame sfocato dal video producer.
        - Converte il frame in spazio colore HSV.
        - Crea una maschera utilizzando i punti e i colori del tavolo.
        - Rileva le palle nella maschera corrente e aggiorna la cronologia delle maschere delle palle.
        - Se la cronologia delle maschere delle palle contiene 3 elementi, calcola il conteggio del movimento corrente.
        - Aggiorna la cronologia dei conteggi del movimento.
        - Se la cronologia dei conteggi del movimento contiene `NUMBER_OF_MOTION_COUNT` elementi, verifica se tutti i conteggi del movimento sono falsi.
            - Se tutti i conteggi del movimento sono falsi, chiama `stop_movement_callback`.
            - Altrimenti, chiama `start_movement_callback`.
        """
        balls_mask_history = CircularArray(
            3
        )  # TODO: Qui memorizzo massimo 3 frame, sarebbe meglio non usare un magic number ma bisognerebbe cambiare l'algoritmo di rilevamento movimento per gestire più frame.
        motion_history = CircularArray(
            self.NUMBER_OF_MOTION_COUNT
        )  # Il motion_count viene calcolato inizialmente su 3 frame, ma poi viene calcolato ad ogni frame, perchè ad ogni frame vengono usati i due frame precedenti per calcolarlo. Quindi aumentando il NUMBER_OF_MOTION_COUNT su quanti frame non si vuole il movimento, valori troppo bassi sono più soggetti a rumore, valori troppo alti potrebbero ritardare l'interruzione del timer.

        isMoving = False
        while self._video_producer.is_opened() and not self._end_event.is_set():
            time.sleep(0.17)
            if not self._is_running.is_set():
                # TODO: Non è necessario sta cosa del motion history
                # Resetto gli array, perchè il video consumer potrebbe rimanere per tanti frame fermo e non voglio che valori vecchi dell'array vengono usati per determinare il movimento nuovo
                balls_mask_history = CircularArray(3)
                motion_history = CircularArray(self.NUMBER_OF_MOTION_COUNT)
                continue
            blurred = self._video_producer.get_frame_blurred()

            hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
            current_balls_mask = self._create_mask(
                hsv, self.table.points, self.table.colors
            )

            balls_mask_history.add(current_balls_mask)
            if balls_mask_history.get_len() == 3:
                current_motion = self._motion_count(balls_mask_history.get_array())
                # Debug: Visualizza se è in movimento o no

                test_image = blurred.copy()
                text = "MOVIMENTO" if current_motion else "FERMO"
                cv2.putText(
                    img=test_image,
                    text=text,
                    org=(10, 30),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=1,
                    color=(255, 255, 255),
                    thickness=2,
                    lineType=cv2.LINE_AA,
                )
                cv2.imshow("Blurred with movement", test_image)
                cv2.waitKey(4)

                if current_motion != isMoving:
                    isMoving = current_motion
                    if isMoving:
                        self.start_movement_callback()
                    else:
                        self.stop_movement_callback()

    CURRENT_MOTION_THRESHOLD = 50

    def _motion_count(self, balls_mask_history):
        """
        Determina se c'è stato movimento tra i frame delle biglie rilevate.

        Args:
            balls_mask_history (CircularArray): Una struttura dati contenente le maschere delle biglie rilevate nei tre frame più recenti.

        Returns:
            bool: True se c'è stato movimento, False altrimenti.
        """
        frame_p2 = balls_mask_history[0]  # Frame -2
        frame_p1 = balls_mask_history[1]  # Frame -1
        frame_c = balls_mask_history[2]  # Frame corrente
        diff1 = cv2.absdiff(frame_p1, frame_p2)
        diff2 = cv2.absdiff(frame_c, frame_p1)
        white_pixel_frame_d1 = cv2.countNonZero(diff1)
        white_pixel_frame_d2 = cv2.countNonZero(diff2)
        max_white_pixel = max(white_pixel_frame_d1, white_pixel_frame_d2)
        return max_white_pixel > self.CURRENT_MOTION_THRESHOLD

    CIRCULARITY_THRESHOLD = 0.7
    H_DIFF, S_DIFF, V_DIFF = 5, 10, 5

    def _create_mask(self, hsv, points, colors):
        """
        Crea una maschera considerando solo le biglie da gioco.

        Questa funzione prende un'immagine HSV (formato OpenCV), un insieme di punti che definiscono un poligono,
        e una lista di colori del tavolo. Crea una maschera che combina due filtri:

        1. Una maschera poligonale basata sui punti forniti
        2. Una maschera di intervallo di colore basata sui colori del tavolo forniti

        Dopo, vengono calcolati i contorni che superano una certa circolarità e viene creata una maschera contenente tali contorni (filled)

        Args:
            hsv (MatLike): Frame da cui ricavare la maschera. Deve essere in formato HSV (formato OpenCV)

            points (List[Tuple(int, int)]): I 4 punti (x,y) che descrivono il rettangolo che delimita il tavolo da gioco. I punti devono essere ordinati in senso orario.

            colors (List[Tuple(int,int,int)]): Un array di colori scritti in HSV (formato OpenCV) che descrivono il tavolo da gioco

        Returns:
            MatLike: Una maschera contenente i contorni delle biglie rilevate.
        """
        color_lower = tuple(
            min(color[i] for color in colors) - diff
            for i, diff in enumerate([self.H_DIFF, self.S_DIFF, self.V_DIFF])
        )
        color_upper = tuple(
            max(color[i] for color in colors) + diff
            for i, diff in enumerate([self.H_DIFF, self.S_DIFF, self.V_DIFF])
        )
        points = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
        rec_mask = cv2.fillPoly(np.zeros(hsv.shape[:2], dtype=np.uint8), [points], 255)
        color_mask = cv2.inRange(hsv, color_lower, color_upper)
        # color_mask = cv2.erode(color_mask, None, iterations=3)
        color_mask = cv2.dilate(color_mask, None, iterations=2)
        color_mask = cv2.bitwise_not(color_mask)  # Inverti la color mask
        combined_mask = cv2.bitwise_and(color_mask, rec_mask)

        contours, _ = cv2.findContours(
            combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        # contours = imutils.grab_contours(contours)
        circularity_mask = np.zeros_like(combined_mask)

        for c in contours:
            area = cv2.contourArea(c)
            perimeter = cv2.arcLength(c, True)
            if perimeter == 0:
                continue
            circularity = 4 * np.pi * area / perimeter**2

            if circularity > self.CIRCULARITY_THRESHOLD:
                cv2.drawContours(circularity_mask, [c], -1, 255, thickness=cv2.FILLED)
        # Debug: Visualizza le maschere intermedie
        cv2.imshow("Color Mask", color_mask)
        cv2.imshow("Rec Mask", rec_mask)
        cv2.imshow("Combined Mask", combined_mask)
        cv2.imshow("Circularity Mask", circularity_mask)
        return circularity_mask
