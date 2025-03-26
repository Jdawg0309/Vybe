from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from flask_socketio import SocketIO

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)

    app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB file size limit
    
    # Make sure the upload folder exists
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'])
    except OSError:
        pass

    # Load environment variables from .env file
    load_dotenv()

    # Get database credentials from environment variables
    db_username = os.getenv('DB_USERNAME', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME', 'vybe-db')

    try:
        db_port = int(db_port)
    except ValueError:
        raise ValueError("Invalid DB_PORT value. Ensure it is a valid integer.")

    # Set SQLAlchemy database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)

    # Register Blueprints
    from . import sockets
    from .auth import auth
    from .profile import profile
    from .friends import friends
    from .messages import messages_bp  # Updated import
    from .notifications import notifications

    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(profile, url_prefix="/")
    app.register_blueprint(friends, url_prefix="/")
    app.register_blueprint(messages_bp, url_prefix="/")  # Updated registration
    app.register_blueprint(notifications, url_prefix="/")

    # Import models
    from .models import User, Friends, Notifications, Messages

    # Create database tables
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.error(f"Failed to create database tables: {e}")
            raise

    # Configure login manager
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app