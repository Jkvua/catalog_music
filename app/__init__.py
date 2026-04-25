from flask import Flask
from app.extensions import db, migrate, ma, jwt
from .errors import register_errors
from config import DevelopmentConfig, TestingConfig, ProductionConfig

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        from . import models

    from .routes.main import main_bp
    app.register_blueprint(main_bp)

    from .routes.usuario import usuario_bp
    app.register_blueprint(usuario_bp)

    from .routes.artista import artista_bp
    app.register_blueprint(artista_bp)

    from .routes.album import album_bp
    app.register_blueprint(album_bp)

    from .routes.avaliacao import avaliacao_bp
    app.register_blueprint(avaliacao_bp)

    from .routes.musica import musica_bp
    app.register_blueprint(musica_bp)

    register_errors(app)

    return app
