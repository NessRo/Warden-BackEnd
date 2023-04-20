from flask import Flask
from config import Config
from extensions import db, migrate
from app.routes import bp_questionaire_templates
from app.models.admin import prepare_base, print_table_names

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Prepare and reflect the schema
    with app.app_context():
        prepare_base()

    # Register blueprints
    app.register_blueprint(bp_questionaire_templates)

    return app
