"""
Main entry point for Clean Architecture version.
This demonstrates how to bootstrap the application with dependency injection.
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_restful import Api
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

from device.video_producer import VideoProducer
from src.infrastructure.di_container import DIContainer
from src.infrastructure.api.game_controller import GameController, GameActionsController


# Load environment variables
load_dotenv()


# Define base model for SQLAlchemy
class Base(DeclarativeBase):
    pass


# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)


def create_app():
    """
    Application factory that creates and configures the Flask app
    using Clean Architecture principles.
    """
    # Create Flask app
    app = Flask(__name__, static_folder="", template_folder="")
    
    # Configure Flask
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shotclock.db"
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
    
    # Initialize database
    db.init_app(app)
    with app.app_context():
        db.create_all()
    
    # Initialize Flask extensions
    api = Api(app)
    CORS(app, supports_credentials=True)
    
    # Initialize SocketIO
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
    
    # Initialize VideoProducer
    video_producer = VideoProducer.get_instance()
    
    # Create Dependency Injection Container
    container = DIContainer(
        db=db,
        video_producer=video_producer,
        socketio=socketio,
    )
    
    # Register API routes (Clean Architecture endpoints)
    # Flask-RESTful will instantiate the resource class for each request
    api.add_resource(
        GameController,
        "/api/v2/game",
        resource_class_kwargs={'container': container}
    )
    api.add_resource(
        GameActionsController,
        "/api/v2/game/actions",
        resource_class_kwargs={'container': container}
    )
    
    # You can also register legacy endpoints for backward compatibility
    # from device.api import resources
    # api.add_resource(resources.GameResource, "/game")
    # etc.
    
    return app, socketio, container


def start_server(debug=False):
    """
    Start the Flask application server.
    
    Args:
        debug: Enable debug mode if True
    """
    app, socketio, container = create_app()
    
    try:
        print("Starting ShotClock server with Clean Architecture...")
        print("API endpoints:")
        print("  - POST   /api/v2/game          - Create game")
        print("  - GET    /api/v2/game          - Get game status")
        print("  - DELETE /api/v2/game          - End game")
        print("  - POST   /api/v2/game/actions  - Game actions (start/pause/resume/increment)")
        
        socketio.run(
            app,
            allow_unsafe_werkzeug=True,
            host="0.0.0.0",
            port=5000,
            debug=debug,
            use_reloader=False,
        )
    except KeyboardInterrupt:
        print("\nShutting down...")
        container.cleanup()
    finally:
        container.cleanup()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        prog="ShotClock Clean Architecture",
        description="ShotClock server using Clean Architecture principles",
    )
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    start_server(debug=args.debug)
