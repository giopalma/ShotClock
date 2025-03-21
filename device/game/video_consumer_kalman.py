from threading import Event, Thread
import time
import cv2
import numpy as np
import logging
from device.video_producer import VideoProducer
from device.table import TablePreset
from device.utils import CircularArray


class BallTracker:
    """
    Implementa un tracciatore di biglie utilizzando il filtro di Kalman.
    Stima posizione, velocità e accelerazione della biglia.
    """

    def __init__(self):
        # Stato: [x, y, dx, dy, ddx, ddy]
        # x, y: posizione
        # dx, dy: velocità
        # ddx, ddy: accelerazione
        self.kalman = cv2.KalmanFilter(6, 2)

        # Matrice di transizione (modello fisico del movimento)
        self.kalman.transitionMatrix = np.array(
            [
                [1, 0, 1, 0, 0.5, 0],  # x = x + dx + 0.5*ddx
                [0, 1, 0, 1, 0, 0.5],  # y = y + dy + 0.5*ddy
                [0, 0, 1, 0, 1, 0],  # dx = dx + ddx
                [0, 0, 0, 1, 0, 1],  # dy = dy + ddy
                [0, 0, 0, 0, 1, 0],  # ddx = ddx
                [0, 0, 0, 0, 0, 1],  # ddy = ddy
            ],
            np.float32,
        )

        # Matrice di misurazione (osserviamo solo x e y)
        self.kalman.measurementMatrix = np.array(
            [[1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0]], np.float32
        )

        # Inizializzazione delle matrici di covarianza - Diminuisco il rumore di processo
        self.kalman.processNoiseCov = (
            np.eye(6, dtype=np.float32) * 0.01
        )  # Ridotto da 0.03
        self.kalman.measurementNoiseCov = np.eye(2, dtype=np.float32) * 0.1

        # Inizializzazione dello stato del filtro
        self.kalman.errorCovPost = np.eye(6, dtype=np.float32)

        self.has_prediction = False
        self.last_prediction = None
        self.last_measurement = None
        self.age = 0  # Età del tracciatore in frame
        self.missed_updates = 0  # Conteggio degli aggiornamenti mancati
        self.is_moving = False
        self.motion_history = CircularArray(5)  # Storia del movimento per stabilizzare

        # Aggiungi una soglia minima di stabilità prima di considerare il tracciatore valido
        self.is_stable = False
        self.stability_count = 0
        self.MIN_STABILITY_FRAMES = 5

    def update(self, position):
        """
        Aggiorna il filtro con la nuova posizione misurata.

        Args:
            position: Tupla (x, y) della posizione misurata, o None se nessuna misura disponibile

        Returns:
            Tupla (x, y) della posizione stimata
        """
        self.age += 1

        # Predizione
        prediction = self.kalman.predict()
        pred_x, pred_y = prediction[0, 0], prediction[1, 0]

        if position is None:
            # Nessuna misura, incrementa contatore dei frame mancati
            self.missed_updates += 1
            self.stability_count = max(
                0, self.stability_count - 1
            )  # Diminuisci stabilità

            # Calcola velocità dalla predizione
            if self.has_prediction:
                dx, dy = prediction[2, 0], prediction[3, 0]
                speed = np.sqrt(dx**2 + dy**2)
                # Diminuisco la soglia per rilevare anche movimenti più lenti
                self.motion_history.add(speed > 4.0)  # Ridotta da 8.0 a 4.0

                # Determina se in movimento (almeno 3/5 dei frame recenti mostrano movimento)
                if self.motion_history.get_len() >= 3:
                    self.is_moving = (
                        sum(self.motion_history.get_array()) >= 3
                    )  # Ridotto da 4 a 3

            self.last_prediction = (pred_x, pred_y)
            self.has_prediction = True
            return (pred_x, pred_y)

        # Aggiorna con nuova misura
        self.missed_updates = 0
        self.last_measurement = position
        measurement = np.array([[position[0]], [position[1]]], dtype=np.float32)

        # Correggi la stima
        self.kalman.correct(measurement)

        # Ricalcola la predizione
        prediction = self.kalman.predict()
        pred_x, pred_y = prediction[0, 0], prediction[1, 0]

        # Calcola velocità e determina stato di movimento
        dx, dy = prediction[2, 0], prediction[3, 0]
        speed = np.sqrt(dx**2 + dy**2)
        # Diminuisco la soglia per rilevare anche movimenti più lenti
        self.motion_history.add(speed > 4.0)  # Ridotta da 8.0 a 4.0

        # Determina movimento (stabile su una finestra temporale)
        if self.motion_history.get_len() >= 3:
            self.is_moving = (
                sum(self.motion_history.get_array()) >= 3
            )  # Ridotto da 4 a 3

        # Aggiorna contatore di stabilità
        if speed < 3.0:  # Se la velocità è bassa, il tracker è stabile
            self.stability_count += 1
            if self.stability_count >= self.MIN_STABILITY_FRAMES:
                self.is_stable = True
        else:
            self.stability_count = max(0, self.stability_count - 1)

        self.last_prediction = (pred_x, pred_y)
        self.has_prediction = True
        return (pred_x, pred_y)

    def is_valid(self):
        """Verifica se il tracciatore è ancora valido (non ha perso la biglia troppo a lungo)"""
        # Un tracker è valido solo se ha avuto abbastanza aggiornamenti per essere stabile
        # oppure è nuovo ma non ha perso troppi aggiornamenti
        return (self.is_stable and self.missed_updates < 10) or (
            self.age < 10 and self.missed_updates < 3
        )

    def get_state(self):
        """Ottiene lo stato completo del tracciatore"""
        state = self.kalman.statePost
        return {
            "position": (state[0, 0], state[1, 0]),
            "velocity": (state[2, 0], state[3, 0]),
            "acceleration": (state[4, 0], state[5, 0]),
            "speed": np.sqrt(state[2, 0] ** 2 + state[3, 0] ** 2),
            "is_moving": self.is_moving,
            "age": self.age,
            "missed_updates": self.missed_updates,
        }


class VideoConsumerKalman:
    """
    Versione migliorata di VideoConsumer che utilizza filtri di Kalman per tracciare le biglie.
    Rileva il movimento in modo più robusto e fornisce informazioni sulla velocità e direzione.
    """

    # Configurazione
    CIRCULARITY_THRESHOLD = 0.75  # Ridotto da 0.8 a 0.75 per essere meno selettivi
    H_DIFF, S_DIFF, V_DIFF = 5, 10, 5  # Differenze per il filtro colore in HSV
    MIN_STATE_CHANGE_INTERVAL = 0.6  # Ridotto da 0.8 a 0.6 secondi
    MAX_TRACKERS = 10  # Numero massimo di tracciatori attivi contemporaneamente

    # Debug
    DEBUG_VISUALIZATIONS = True  # Abilita finestre di debug

    def __init__(
        self,
        table: TablePreset,
        start_movement_callback,
        stop_movement_callback,
        video_producer: VideoProducer,
    ):
        """
        Inizializza il VideoConsumerKalman.

        Args:
            table (TablePreset): Preset del tavolo contenente punti, colori e soglia area minima.
            start_movement_callback (callable): Funzione chiamata al rilevamento del movimento.
            stop_movement_callback (callable): Funzione chiamata al passaggio allo stato fermo.
            video_producer (VideoProducer): Istanza del produttore video.
        """
        self.table = table
        self.start_movement_callback = start_movement_callback
        self.stop_movement_callback = stop_movement_callback
        self._video_producer = video_producer

        # Configurazione da TablePreset
        self.min_area_threshold = table.min_area_threshold

        # Eventi per controllo thread
        self._is_running = Event()
        self._is_running.clear()
        self._end_event = Event()

        # Stato interno
        self.is_moving = False
        self._last_state_change_time = 0
        self._fps_history = CircularArray(30)
        self._ball_trackers = []  # Lista di tracciatori attivi
        self._global_motion_history = CircularArray(10)  # Storia movimento globale

        # Avvia thread
        self._thread = Thread(target=self.run, name="VideoConsumerKalmanThread")
        self._thread.daemon = False
        self._thread.start()

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
            self._is_running.set()  # Sblocca il thread se è in attesa

            # Chiudi le finestre di debug
            if self.DEBUG_VISUALIZATIONS:
                cv2.destroyAllWindows()

    def run(self):
        """
        Ciclo principale del VideoConsumerKalman.
        Traccia le biglie utilizzando filtri di Kalman e determina il movimento
        in base alle velocità stimate.
        """
        try:
            last_time = time.time()

            while self._video_producer.is_opened() and not self._end_event.is_set():
                # Calcola FPS
                current_time = time.time()
                dt = current_time - last_time
                fps = 1.0 / dt if dt > 0 else 0
                self._fps_history.add(fps)
                last_time = current_time

                # Gestione pausa
                if not self._is_running.is_set():
                    time.sleep(0.05)
                    # Reset tracciatori quando in pausa
                    self._ball_trackers = []
                    self._global_motion_history = CircularArray(10)
                    continue

                # Elaborazione frame con gestione degli errori
                try:
                    # Adatta sleep in base al FPS desiderato (target 20 FPS)
                    avg_fps = sum(self._fps_history.get_array()) / max(
                        1, self._fps_history.get_len()
                    )
                    if avg_fps > 22:
                        time.sleep(0.01)  # Rallenta se troppo veloce

                    # Ottieni frame e preelaborazione
                    blurred = self._video_producer.get_frame_blurred()
                    if blurred is None:
                        time.sleep(0.05)
                        continue

                    # Converti in HSV
                    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

                    # Crea maschera e trova biglie
                    balls_mask = self._create_mask(
                        hsv, self.table.points, self.table.colors
                    )
                    detected_balls = self._detect_balls(balls_mask)

                    # Aggiorna i tracciatori esistenti e ne crea di nuovi se necessario
                    self._update_trackers(detected_balls)

                    # Determina lo stato di movimento globale
                    self._update_motion_state()

                    # Visualizzazioni di debug
                    if self.DEBUG_VISUALIZATIONS:
                        self._debug_visualizations(blurred, balls_mask, detected_balls)

                except Exception as e:
                    logging.error(f"Errore nell'elaborazione del frame: {e}")
                    time.sleep(0.1)

        except Exception as e:
            logging.error(f"Errore critico nel thread VideoConsumerKalman: {e}")
        finally:
            if self.DEBUG_VISUALIZATIONS:
                cv2.destroyAllWindows()

    def _create_mask(self, hsv, points, colors):
        """
        Crea una maschera per rilevare le biglie basata sui colori e forma del tavolo.

        Args:
            hsv: Frame in formato HSV
            points: Punti che definiscono i bordi del tavolo
            colors: Colori del tavolo in formato HSV

        Returns:
            Maschera contenente le biglie rilevate
        """
        # Definisce l'intervallo di colore
        color_lower = tuple(
            min(color[i] for color in colors) - diff
            for i, diff in enumerate([self.H_DIFF, self.S_DIFF, self.V_DIFF])
        )
        color_upper = tuple(
            max(color[i] for color in colors) + diff
            for i, diff in enumerate([self.H_DIFF, self.S_DIFF, self.V_DIFF])
        )

        # Crea maschera del tavolo
        points_np = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
        table_mask = cv2.fillPoly(
            np.zeros(hsv.shape[:2], dtype=np.uint8), [points_np], 255
        )

        # Crea maschera di colore e inverte
        color_mask = cv2.inRange(hsv, color_lower, color_upper)
        color_mask = cv2.dilate(color_mask, None, iterations=2)
        color_mask = cv2.bitwise_not(color_mask)

        # Combina maschere
        combined_mask = cv2.bitwise_and(color_mask, table_mask)

        # Visualizza se in debug
        if self.DEBUG_VISUALIZATIONS:
            cv2.imshow("Table Mask", table_mask)
            cv2.imshow("Color Mask", color_mask)
            cv2.imshow("Combined Mask", combined_mask)

        return combined_mask

    def _detect_balls(self, mask):
        """
        Rileva le biglie dalla maschera applicando filtri di forma e dimensione.

        Args:
            mask: Maschera binaria contenente i potenziali oggetti

        Returns:
            Lista di tuple (x, y) contenenti le posizioni delle biglie rilevate
        """
        # Trova contorni
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filtra per area e circolarità
        detected_balls = []
        for contour in contours:
            area = cv2.contourArea(contour)

            # Filtra per area minima (ridotta per rilevare più biglie)
            if area < self.min_area_threshold * 1.1:  # Ridotto da 1.2 a 1.1
                continue

            # Calcola circolarità
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue

            circularity = 4 * np.pi * area / (perimeter**2)

            # Accetta solo forme circolari
            if circularity > self.CIRCULARITY_THRESHOLD:
                # Calcola centro
                M = cv2.moments(contour)
                if M["m00"] > 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    detected_balls.append((cx, cy, area))

        # Ordina per area (più grandi prima)
        detected_balls.sort(key=lambda x: x[2], reverse=True)

        # Limita il numero massimo di biglie rilevate per evitare falsi positivi
        detected_balls = detected_balls[:15]  # max 15 biglie sul tavolo

        # Ritorna solo coordinate (x, y)
        return [(x, y) for x, y, _ in detected_balls]

    def _update_trackers(self, detected_balls):
        """
        Aggiorna i tracciatori esistenti con le nuove posizioni o ne crea di nuovi se necessario.
        Gestisce l'associazione tra tracciatori e biglie rilevate.

        Args:
            detected_balls: Lista di tuple (x, y) con le posizioni delle biglie rilevate
        """
        # Rimuovi tracciatori non più validi
        self._ball_trackers = [
            tracker for tracker in self._ball_trackers if tracker.is_valid()
        ]

        # Limita numero massimo di tracker attivi
        if len(self._ball_trackers) > self.MAX_TRACKERS:
            # Mantieni solo i più stabili o più vecchi
            self._ball_trackers.sort(
                key=lambda t: t.stability_count + t.age / 10, reverse=True
            )
            self._ball_trackers = self._ball_trackers[: self.MAX_TRACKERS]

        if not detected_balls:
            # Nessuna biglia rilevata, aggiorna i tracciatori con None
            for tracker in self._ball_trackers:
                tracker.update(None)
            return

        if not self._ball_trackers:
            # Primo rilevamento o dopo reset, crea nuovi tracciatori
            for ball_pos in detected_balls[: self.MAX_TRACKERS]:
                tracker = BallTracker()
                tracker.update(ball_pos)
                self._ball_trackers.append(tracker)
            return

        # Associa biglie rilevate ai tracciatori esistenti utilizzando distanza minima
        # Matrice delle distanze
        distance_matrix = np.zeros((len(self._ball_trackers), len(detected_balls)))
        for i, tracker in enumerate(self._ball_trackers):
            for j, ball_pos in enumerate(detected_balls):
                if tracker.last_prediction:
                    dx = tracker.last_prediction[0] - ball_pos[0]
                    dy = tracker.last_prediction[1] - ball_pos[1]
                    distance_matrix[i, j] = np.sqrt(dx**2 + dy**2)
                else:
                    distance_matrix[i, j] = float("inf")

        # Assegna biglie ai tracciatori
        assigned_balls = set()

        for i, tracker in enumerate(self._ball_trackers):
            # Trova la biglia più vicina non ancora assegnata
            valid_distances = [
                (j, distance_matrix[i, j])
                for j in range(len(detected_balls))
                if j not in assigned_balls
            ]

            if valid_distances:
                j, dist = min(valid_distances, key=lambda x: x[1])

                # Aggiorna solo se la distanza è ragionevole (ridotta)
                if dist < 30:  # Ridotta da 50 a 30 pixel
                    tracker.update(detected_balls[j])
                    assigned_balls.add(j)
                else:
                    tracker.update(None)
            else:
                tracker.update(None)

        # Crea nuovi tracciatori per le biglie non assegnate
        # Solo se ce ne sono pochi e solo per oggetti sufficientemente grandi
        if len(self._ball_trackers) < self.MAX_TRACKERS * 0.7:  # max 70% della capacità
            for j, ball_pos in enumerate(detected_balls):
                if (
                    j not in assigned_balls
                    and len(self._ball_trackers) < self.MAX_TRACKERS
                ):
                    tracker = BallTracker()
                    tracker.update(ball_pos)
                    self._ball_trackers.append(tracker)

    def _update_motion_state(self):
        """
        Determina lo stato globale di movimento in base ai tracciatori attivi.
        Applica un debounce temporale per evitare cambi di stato troppo frequenti.
        """
        # Determina se almeno una biglia è in movimento
        balls_moving = any(tracker.is_moving for tracker in self._ball_trackers)

        # Aggiorna la storia del movimento
        self._global_motion_history.add(balls_moving)

        # Determina il movimento con debounce
        if self._global_motion_history.get_len() >= 5:
            history = self._global_motion_history.get_array()
            # Ridotta la soglia per essere più sensibili
            new_moving_state = (
                sum(history) / len(history) >= 0.6
            )  # Ridotta da 0.75 a 0.6

            # Applica debounce temporale
            current_time = time.time()
            if (
                new_moving_state != self.is_moving
                and (current_time - self._last_state_change_time)
                > self.MIN_STATE_CHANGE_INTERVAL
            ):
                self.is_moving = new_moving_state
                self._last_state_change_time = current_time

                # Invoca callbacks
                if new_moving_state:
                    logging.info("Movimento rilevato (Kalman)")
                    self.start_movement_callback()
                else:
                    logging.info("Movimento terminato (Kalman)")
                    self.stop_movement_callback()

    def _debug_visualizations(self, frame, balls_mask, detected_balls):
        """
        Crea visualizzazioni di debug per monitorare il funzionamento dell'algoritmo.

        Args:
            frame: Frame BGR originale
            balls_mask: Maschera delle biglie
            detected_balls: Posizioni delle biglie rilevate
        """
        # Crea immagine di debug
        debug_image = frame.copy()

        # Calcola FPS medio
        avg_fps = sum(self._fps_history.get_array()) / max(
            1, self._fps_history.get_len()
        )

        # Visualizza info di stato
        cv2.putText(
            debug_image,
            f"{'MOVIMENTO' if self.is_moving else 'FERMO'} - FPS: {avg_fps:.1f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2,
            cv2.LINE_AA,
        )

        # Disegna biglie rilevate
        for x, y in detected_balls:
            cv2.circle(debug_image, (x, y), 10, (0, 255, 0), 1)

        # Disegna tracciatori attivi - sia stabili che in movimento
        for i, tracker in enumerate(self._ball_trackers):
            if not tracker.last_prediction:
                continue

            # Mostriamo ora tutti i tracker ad eccezione di quelli molto giovani e instabili
            if not tracker.is_stable and tracker.age < 3:
                continue

            # Estrai stato del tracciatore
            state = tracker.get_state()
            x, y = int(state["position"][0]), int(state["position"][1])
            vx, vy = state["velocity"]
            speed = state["speed"]

            # Calcola colore in base allo stato (rosso se in movimento, blu se fermo)
            color = (0, 0, 255) if tracker.is_moving else (255, 0, 0)

            # Disegna posizione stimata e vettore velocità
            cv2.circle(debug_image, (x, y), 12, color, 2)
            cv2.putText(
                debug_image,
                f"{i}",
                (x - 5, y + 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            # Disegna vettore di velocità solo se significativo
            if speed > 2.0:  # Ridotto da 3.0 a 2.0
                end_x = int(x + vx * 2)
                end_y = int(y + vy * 2)
                cv2.arrowedLine(debug_image, (x, y), (end_x, end_y), color, 2)

        # Visualizza le immagini di debug
        cv2.imshow("Ball Tracking (Kalman)", debug_image)
        cv2.imshow("Balls Mask", balls_mask)

        # Gestione input tastiera per debug
        key = cv2.waitKey(1)
        if key == ord("p"):  # Pausa
            while cv2.waitKey(100) != ord("p"):
                pass  # Attendi fino alla pressione di 'p' nuovamente
