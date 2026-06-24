from flask import Flask
from flask_cors import CORS
from .config import config


def create_app(config_name: str = 'default') -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    CORS(app, origins=[app.config['FRONTEND_URL']])

    from .routes import health_bp, chat_bp, emails_bp, memory_bp, tts_bp
    app.register_blueprint(health_bp)
    app.register_blueprint(chat_bp, url_prefix="/api")
    app.register_blueprint(emails_bp, url_prefix="/api")
    app.register_blueprint(memory_bp, url_prefix="/api")
    app.register_blueprint(tts_bp, url_prefix="/api")

    return app
