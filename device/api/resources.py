import queue
from flask import jsonify, request, Response
from flask_restful import Resource
import json
import logging
import cv2
import time
from flask import send_file
import os
import threading
import numpy as np
import uuid

from device.api.auth import auth_required, create_access_token
from device.config import get_config
from device.utils import hex_to_opencv_hsv
from device.video_producer import VideoProducer
from device.game import game_manager
from device.api import db
from device.api import models_dao


class VideoFrameResource(Resource):
    def get(self):
        frame = VideoProducer.get_instance().get_frame()
        _, buffer = cv2.imencode(".jpg", frame)
        response = Response(buffer.tobytes(), mimetype="image/jpeg")
        return response

    def post(self):
        def mask(hsv, colors, points):
            # Funzione per mascherare l'immagine HSV
            # Se non ci sono colori, applica solo la maschera del poligono
            if not colors:
                # Crea una maschera con il poligono
                points = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
                rec_mask = cv2.fillPoly(
                    np.zeros(hsv.shape[:2], dtype=np.uint8), [points], 255
                )
                rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
                return cv2.bitwise_and(rgb, rgb, mask=rec_mask)

            colors = [hex_to_opencv_hsv(color) for color in colors]
            color_lower = tuple(
                min(color[i] for color in colors) - diff
                for i, diff in enumerate([5, 10, 5])
            )
            color_upper = tuple(
                max(color[i] for color in colors) + diff
                for i, diff in enumerate([5, 10, 5])
            )
            points = np.array(points, dtype=np.int32).reshape((-1, 1, 2))

            rec_mask = cv2.fillPoly(
                np.zeros(hsv.shape[:2], dtype=np.uint8), [points], 255
            )
            color_mask = cv2.inRange(hsv, color_lower, color_upper)
            color_mask = cv2.dilate(color_mask, None, iterations=2)
            color_mask = cv2.bitwise_not(color_mask)

            combined_mask = cv2.bitwise_and(color_mask, rec_mask)
            rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            return cv2.bitwise_and(rgb, rgb, mask=combined_mask)

        data = request.json
        if "colors" in data and "points" in data:
            colors = data["colors"]
            points = data["points"]
            if len(points) > 2:
                frame = VideoProducer.get_instance().get_frame()
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                hsv = cv2.GaussianBlur(hsv, (5, 5), 0)
                masked = mask(hsv, colors, points)
                blurred = cv2.GaussianBlur(masked, (5, 5), 0)
                _, buffer = cv2.imencode(".jpg", blurred)
                response = Response(buffer.tobytes(), mimetype="image/jpeg")
                return response


class VideoRecordResource(Resource):
    def get(self):
        recording_id = str(uuid.uuid4())
        video_path = os.path.join(os.getcwd(), f"output_{recording_id}.avi")

        def record_video(video_path):
            logging.info(f"Video Recording Started: {video_path}")
            video_producer = VideoProducer.get_instance()
            start_time = time.time()

            try:
                # Crea subito il VideoWriter
                dummy_frame = video_producer.get_frame()
                height, width = dummy_frame.shape[:2]

                # Assicurati che la directory esista
                os.makedirs(os.path.dirname(video_path), exist_ok=True)

                out = cv2.VideoWriter(
                    video_path, cv2.VideoWriter_fourcc(*"XVID"), 30, (width, height)
                )

                while time.time() - start_time < 50:
                    frame = video_producer.get_frame()
                    # Scrive direttamente il frame invece di tenerlo in memoria
                    out.write(frame)
                    # Usa una pausa standard invece di eventlet.sleep
                    time.sleep(0.01)  # Pausa più breve per una migliore framerate

                out.release()
                logging.info(f"Video salvato con successo: {video_path}")

            except Exception as e:
                logging.error(f"Errore durante la registrazione: {e}")

        # Avvia la funzione di registrazione in un thread standard Python
        thread = threading.Thread(target=record_video, args=(video_path,), daemon=True)
        thread.start()

        return jsonify(
            {
                "message": "Video recording started in background",
                "recording_id": recording_id,
                "file_path": video_path,
            }
        )


class VideoStreamResource(Resource):
    # Coda condivisa per i frame
    frame_queue = queue.Queue(maxsize=10)
    # Variabile per tenere traccia se il thread di acquisizione è attivo
    is_capturing = False
    # Lock per accesso sicuro alle variabili condivise
    lock = threading.Lock()
    # Riferimento al thread di acquisizione
    capture_thread = None

    @classmethod
    def start_capture_thread(cls):
        """Avvia il thread di acquisizione frame se non è già in esecuzione"""
        with cls.lock:
            if not cls.is_capturing:
                cls.is_capturing = True
                cls.capture_thread = threading.Thread(
                    target=cls.capture_frames, daemon=True
                )
                cls.capture_thread.start()
                return True
            return False

    @classmethod
    def stop_capture_thread(cls):
        """Ferma il thread di acquisizione in modo sicuro"""
        with cls.lock:
            was_capturing = cls.is_capturing
            cls.is_capturing = False
            # Svuota la coda
            while not cls.frame_queue.empty():
                try:
                    cls.frame_queue.get_nowait()
                except:
                    pass
        return was_capturing

    @classmethod
    def capture_frames(cls):
        """Thread che acquisisce continuamente i frame e li mette in coda"""
        video_producer = VideoProducer.get_instance()
        try:
            while cls.is_capturing:
                frame = video_producer.get_frame()
                if frame is not None:
                    # Se la coda è piena, rimuovi il frame più vecchio
                    if cls.frame_queue.full():
                        try:
                            cls.frame_queue.get_nowait()
                        except queue.Empty:
                            pass
                    # Aggiungi il nuovo frame
                    cls.frame_queue.put(frame)
                time.sleep(0.03)  # Piccola pausa
        except Exception as e:
            print(f"Errore nel thread di acquisizione: {e}")
        finally:
            with cls.lock:
                cls.is_capturing = False

    def get(self):
        # Assicurati che il thread di acquisizione sia in esecuzione
        self.start_capture_thread()

        def generate_frames():
            while self.is_capturing:
                try:
                    # Attendi un frame dalla coda (timeout di 1 secondo)
                    frame = self.frame_queue.get(timeout=1.0)

                    # Converti il frame in formato JPEG
                    ret, buffer = cv2.imencode(".jpg", frame)
                    frame_bytes = buffer.tobytes()

                    # Formato per il multipart/x-mixed-replace
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
                    )

                except queue.Empty:
                    # Se non ci sono frame disponibili, manda un frame vuoto o continua
                    continue
                except Exception as e:
                    print(f"Errore nel generatore: {e}")
                    break

        return Response(
            generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
        )


class VideoStreamControlResource(Resource):
    def post(self):
        # Avvia lo streaming
        if VideoStreamResource.start_capture_thread():
            return jsonify({"status": "success", "message": "Streaming avviato"})
        else:
            return jsonify({"status": "info", "message": "Streaming già in corso"})

    def delete(self):
        # Ferma lo streaming
        if VideoStreamResource.stop_capture_thread():
            return jsonify({"status": "success", "message": "Streaming interrotto"})
        else:
            return jsonify({"status": "info", "message": "Streaming non attivo"})

    def get(self):
        # Controlla lo stato dello streaming
        is_active = VideoStreamResource.is_capturing
        return jsonify({"status": "success", "streaming_active": is_active})


class GameResource(Resource):

    def get(self):
        game = game_manager.get_game()
        if game is None:
            return ({"message": "No game in progress"}, 404)
        else:
            data_return = {
                "player_names": game.player_names,
                "last_remaining_time": game.last_remaining_time,
                "current_increments": game.increments,
                "game_status": game.status,
                "ruleset_id": game.ruleset.id,
                "tablepreset_id": game.table.id,
            }
            return jsonify(data_return)

    @auth_required
    def post(self):
        from . import socketio

        try:
            if not request.is_json:
                return ({"message": "Missing JSON in request"}, 400)
            data = request.json
            if not all(
                flag in data
                for flag in ("ruleset_id", "table_id", "player1_name", "player2_name")
            ):
                return (
                    {
                        "message": "Missing some required fields: ruleset_id, table_id, player1_name, player2_name"
                    },
                    400,
                )
            ruleset = models_dao.RulesetDao.get(data["ruleset_id"])
            table = models_dao.TablePresetDao.get(data["table_id"])
            table.points = json.loads(table.points)
            table.colors = json.loads(table.colors)
            table.colors = [hex_to_opencv_hsv(color) for color in table.colors]
            if ruleset and table:
                game_manager.new_game(
                    ruleset=ruleset,
                    table=table,
                    player1_name=data["player1_name"],
                    player2_name=data["player2_name"],
                    socketio=socketio,
                )
                return ({"message": "Game created successfully"}, 200)
            else:
                return ({"message": "Ruleset or TablePreset not found"}, 404)
        except Exception as e:
            logging.error(e)
            return ({"message": "Internal server error"}, 500)


class GameActionsResource(Resource):
    @auth_required
    def post(self):
        # Prendere il request e vedere se c'è un action
        data = None
        if not request.is_json:
            data = request.form
        else:
            data = request.json

        if "action" not in data:
            return ({"message": "Missing 'action' in request"}, 400)

        game = game_manager.get_game()
        if game is None:
            return ({"message": "No game in progress"}, 400)

        action = data["action"].lower()
        error = None
        if action == "start":
            error = game.start()
        elif action == "pause":
            game.pause()
        elif action == "resume":
            game.resume()
        elif action == "end":
            error = game_manager.end_game()
        elif action == "increment_time_p0":
            error = game.increment_time(0)
        elif action == "increment_time_p1":
            error = game.increment_time(1)
        else:
            return ({"message": "Invalid action"}, 400)
        if error:
            return ({"message": error}, 400)
        return ({"message": f"Action '{action}' performed successfully"}, 200)


class TablePresetResource(Resource):
    def get(self):
        tables = models_dao.TablePresetDao.get_all()
        for table in tables:
            table.colors = json.loads(table.colors)
            table.points = json.loads(table.points)
        return jsonify(tables)

    @auth_required
    def post(self):
        if not request.is_json:
            return ({"message": "Missing JSON in request"}, 400)
        data = request.json
        if not all(
            field in data
            for field in ("name", "points", "colors", "min_area_threshold")
        ):
            return (
                {
                    "message": "Missing required fields: name, points, colors, min_area_threshold"
                },
                400,
            )
        tablepreset = models_dao.TablePresetDao.create(
            name=data["name"],
            points=data["points"],
            colors=data["colors"],
            min_area_threshold=data["min_area_threshold"],
        )
        return jsonify(tablepreset)


class TablePresetResource2(Resource):
    @auth_required
    def delete(self, id):
        if models_dao.TablePresetDao.delete(id):
            return ("TablePreset deleted", 200)
        return ("TablePreset not found", 404)


class RulesetResource(Resource):
    def get(self):
        rulesets = models_dao.RulesetDao.get_all()
        return jsonify(rulesets)

    @auth_required
    def post(self):
        if not request.is_json:
            return ({"message": "Missing JSON in request"}, 400)
        data = request.json
        ruleset = models_dao.RulesetDao.create(
            name=data["name"],
            initial_duration=data["initial_duration"],
            turn_duration=data["turn_duration"],
            allarm_time=data["allarm_time"],
            increment_duration=data["increment_duration"],
            max_increment_for_match=data["max_increment_for_match"],
        )
        return jsonify(ruleset)


class RulesetResource2(Resource):
    @auth_required
    def delete(self, id):
        if models_dao.RulesetDao.delete(id):
            return ("Ruleset deleted", 200)
        return ("Ruleset not found", 404)


class Login(Resource):
    def __init__(self, bcrypt):
        self.bcrypt = bcrypt

    def post(self):
        data = request.get_json()
        password = data.get("password")
        config = get_config()
        hashed_password = config["WEB"]["Password"]
        if self.bcrypt.check_password_hash(hashed_password, password):
            access_token = create_access_token()
            return {"message": "Login successful", "access_token": access_token}, 200
        else:
            return {"message": "Invalid password"}, 401
