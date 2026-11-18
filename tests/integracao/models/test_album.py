import pytest
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models.usuario import Usuario
from app.models.album import Album
from app.models.artista import Artista


def test_salvamento_correto_album(app):
    usuario = Usuario(
        user="usuario_teste",
        email="usuario_teste@email.com",
        password="senha_teste"
    )
    db.session.add(usuario)
    db.session.flush()

    artista = Artista(nome="tyler the creator", usuario_id=usuario.id)
    db.session.add(artista)
    db.session.flush()

    album = Album(
        titulo="Chromakopia",
        ano=2024,
        artista_id=artista.id,
        usuario_id=usuario.id
    )
    db.session.add(album)
    db.session.commit()

    assert album.id is not None
    assert album.id > 0

def test_salvamento_incorreto_album(app):
    usuario = Usuario(
        user="usuario_teste",
        email="usuario_teste@email.com",
        password="senha_teste"
    )
    db.session.add(usuario)
    db.session.flush()

    artista = Artista(nome="mac miller", usuario_id=usuario.id)
    db.session.add(artista)
    db.session.flush()

    album_invalido = Album(
        ano=2016,
        artista_id=artista.id,
        usuario_id=usuario.id
    )
    db.session.add(album_invalido)

    with pytest.raises(IntegrityError):
        db.session.commit()