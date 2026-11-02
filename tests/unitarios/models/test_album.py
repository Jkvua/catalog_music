import pytest
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models.album import Album
from app.models.artista import Artista

def test_instanciar_album():
    titulo_esperado = "Chromakopia"
    ano_esperado = 2024
    artista_id_esperado = 1
    usuario_id_esperado = 2

    album = Album(
        titulo=titulo_esperado,
        ano=ano_esperado,
        artista_id=artista_id_esperado,
        usuario_id=usuario_id_esperado
    )

    assert album.titulo == titulo_esperado
    assert album.ano == ano_esperado
    assert album.artista_id == artista_id_esperado
    assert album.usuario_id == usuario_id_esperado
    assert album.id is None

def test_salvamento_correto_album(app):
    artista = Artista(nome="tyler the creator")
    db.session.add(artista)
    db.session.commit()

    album = Album(titulo="Chromakopia", ano=2024, artista_id=artista.id)
    db.session.add(album)
    db.session.commit()

    assert album.id is not None
    assert album.id > 0

def test_salvamento_incorreto_album(app):
    artista = Artista(nome="mac miller")
    db.session.add(artista)
    db.session.commit()

    album_invalido = Album(ano=2016, artista_id=artista.id)
    db.session.add(album_invalido)

    with pytest.raises(IntegrityError):
        db.session.commit()