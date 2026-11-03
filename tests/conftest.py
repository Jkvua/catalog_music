import pytest
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from app import create_app
from app.extensions import db
from config import TestingConfig

@pytest.fixture
def app():
    """criando e configurando a aplicação para testes"""

    app = create_app(TestingConfig)

    engine = create_engine(TestingConfig.SQLALCHEMY_DATABASE_URI)
    if not database_exists(engine.url):
        create_database(engine.url)

    with app.app_context():
        db.create_all()  # Cria todas as tabelas no banco 'musica_test'
        yield app  # Fornece a aplicação para os testes

        db.session.remove()
        db.drop_all()  # Limpa o banco de dados após os testes

@pytest.fixture
def client(app):
    """Fornece um cliente de teste para a aplicação"""
    return app.test_client()
