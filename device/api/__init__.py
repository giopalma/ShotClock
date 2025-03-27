from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_restful import Api
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from . import websocket

# Carica le variabili d'ambiente
load_dotenv()


# Definisci la classe base del modello. Server per SQLAlchemy
class Base(DeclarativeBase):
    pass


# Inizializza SQLAlchemy con la classe base del modello
db = SQLAlchemy(model_class=Base)

# Importa le risorse dopo aver inizializzato db per evitare importazioni circolari
from . import resources

# Inizializza l'app Flask
app = Flask(__name__, static_folder="", template_folder="")

# Configura l'app Flask
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shotclock.db"
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")

# Inizializza il database con il contesto dell'app
db.init_app(app)
with app.app_context():
    db.create_all()

# Inizializza le estensioni Flask
api = Api(app)
CORS(app)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    logger=True,
    async_mode="threading",
    path="/socket.io",
    ping_timeout=60,
    ping_interval=25,
    engineio_logger=False,
)
websocket.register(socketio)

api.add_resource(resources.GameResource, "/game")
api.add_resource(resources.GameActionsResource, "/game/actions")
api.add_resource(resources.TablePresetResource, "/table")
api.add_resource(resources.TablePresetResource2, "/table/<int:id>")
api.add_resource(resources.RulesetResource, "/ruleset")
api.add_resource(resources.RulesetResource2, "/ruleset/<int:id>")
api.add_resource(resources.VideoFrameResource, "/video/frame")
api.add_resource(resources.VideoRecordResource, "/video/record")
api.add_resource(resources.VideoStreamResource, "/video/stream")
api.add_resource(resources.VideoStreamControlResource, "/video/stream/control")
api.add_resource(resources.Login, "/login")


def start(debug=False):
    """
    Avvia il server API.

    Parametri:
    debug (bool): Se True, il server verrà eseguito in modalità debug. Il valore predefinito è False.
    """
    socketio.run(
        app,
        allow_unsafe_werkzeug=True,
        host="0.0.0.0",
        port=5000,
        debug=debug,
        use_reloader=False,
    )
