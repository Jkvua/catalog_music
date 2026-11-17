import pytest
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models.usuario import Usuario

def test_salvamento_correto_usuario(app):
    usuario = Usuario(user="carlos", email="carlos@carlos.com", password="senha123")

    db.session.add(usuario)
    db.session.commit()

    assert usuario.id is not None
    assert usuario.id > 0
    assert usuario.is_admin is False

def test_email_unico_usuario(app):
    usuario1 = Usuario(user="maria", email="maria@maria.com", password="senha123")
    db.session.add(usuario1)
    db.session.commit()

    usuario2 = Usuario(user="julia", email="maria@maria.com", password="senha123")
    db.session.add(usuario2)

    with pytest.raises(IntegrityError):
        db.session.commit()

def test_salvamento_invalido_usuario(app):
    usuario_invalido = Usuario(user="george", password="senha123")
    db.session.add(usuario_invalido)

    with pytest.raises(IntegrityError):
        db.session.commit()