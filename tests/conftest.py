import pytest
from app import create_app
from app.extensions import db
from config import TestingConfig

@pytest.fixture
def app():
    """criando e configurando a aplicação para testes"""

    app = create_app(TestingConfig)

    with app.app_context():
        db.create_all()  # Cria todas as tabelas no banco 'musica_test'
        yield app  # Fornece a aplicação para os testes

        db.session.remove()
        db.drop_all()  # Limpa o banco de dados após os testes

@pytest.fixture
def client(app):
    """Fornece um cliente de teste para a aplicação"""
    return app.test_client()
