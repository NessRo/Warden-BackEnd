import os

from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db, migrate
from app.routes import bp_questionaire_templates
from app.models.admin import prepare_base

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    allowed_origins = os.getenv('ALLOWED_ORIGINS').split(',')

    CORS(app, origins=allowed_origins)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Prepare and reflect the schema
    with app.app_context():
        prepare_base()

    # Register blueprints
    app.register_blueprint(bp_questionaire_templates)

    return app
