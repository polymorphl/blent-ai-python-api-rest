from flask import Flask
from .config import Config
from .extensions import db, bcrypt, jwt
from .routes.auth import auth_bp


def create_app(config=None):
    # Create the Flask App
    app = Flask(__name__)
    # Set the config
    app.config.from_object(Config)
    if config:
        app.config.from_object(config)
    # Enable bcrypt
    bcrypt.init_app(app)
    # Initialize the app with the extension
    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        from .models import User  # noqa: F401
        db.create_all()

    # Register blueprints
    app.register_blueprint(auth_bp)

    return app
