from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_restful import Api
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

from . import resources, socketio_events


app = Flask(__name__, static_folder="", template_folder="")

# FLASK API CONFIGS
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shotclock.db"

# Inizializzo il database
db.init_app(app)

with app.app_context():
    db.create_all()
api = Api(app)
CORS(app)
socketio = SocketIO(app)
socketio_events.register(socketio)

api.add_resource(resources.GameResource, "/game")
api.add_resource(resources.TablePresetResource, "/table")
api.add_resource(resources.TablePresetResource2, "/table/<int:id>")
api.add_resource(resources.RulesetResource, "/ruleset")
api.add_resource(resources.RulesetResource2, "/ruleset/<int:id>")


def _server_run(debug):
    socketio.run(app, debug=debug)


def start(debug=False):
    """
    Avvia il server API.
    Parameters:
    debug (bool): Se True, il server verrà eseguito in modalità debug. Il valore predefinito è False.
    """
    _server_run(debug)
