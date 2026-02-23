import logging
from flask import Flask, jsonify
from flask_cors import CORS

from backend.config import Config
from backend.repository.database import close_db, init_db, DATABASE_PATH
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def create_app(config=None):
    app = Flask(__name__)
    load_dotenv()

    cfg = config or Config()
    app.config['SECRET_KEY'] = cfg.SECRET_KEY
    app.config['JWT_SECRET_KEY'] = cfg.JWT_SECRET_KEY
    app.config.from_object(Config)

    # CORS
    CORS(app, origins=[cfg.FRONTEND_URL, "http://localhost:3000", "http://127.0.0.1:3000"], supports_credentials=True)

    # Database teardown
    app.teardown_appcontext(close_db)

    # Initialize database
    init_db(app)

    # Register blueprints
    from backend.routes.health import health_bp
    from backend.routes.auth import auth_bp
    from backend.routes.students import students_bp
    from backend.routes.subjects import subjects_bp
    from backend.routes.preferences import preferences_bp
    from backend.routes.ai import ai_bp
    from backend.routes.scheduling import scheduling_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(subjects_bp)
    app.register_blueprint(preferences_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(scheduling_bp)

    # Register error handlers
    from backend.middleware.error_handlers import register_error_handlers
    register_error_handlers(app)

    return app
