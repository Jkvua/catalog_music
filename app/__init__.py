from flask import Flask
from app.extensions import db, migrate  
from config import DevelopmentConfig, TestingConfig, ProductionConfig

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from . import models

    from .routes.artista import artista_bp
    app.register_blueprint(artista_bp)

    return app
