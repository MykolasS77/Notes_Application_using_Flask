from flask import Flask

from flask_cors import CORS
from flask_jwt_extended import JWTManager
from notes_app.jwt_handlers import register_jwt_handlers
from notes_app.models import db
from notes_app.routes import bp


def create_app(import_name):
    app = Flask(import_name)
    CORS(app)

    app.config.from_object("notes_app.config.Config")

    db.init_app(app)
    app.register_blueprint(bp)

    # Create DB tables
    with app.app_context():
        db.create_all()

    # User model already defined above
    jwt = JWTManager(app)
    register_jwt_handlers(jwt)

    return app
