import pytest
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models.artista import Artista
from app.models.album import Album

def test_instanciar_artista():
    nome_esperado = "tyler the creator"
    genero_esperado = "hip hop"
    pais_esperado = "EUA"

    artista = Artista(
        nome=nome_esperado,
        genero=genero_esperado,
        pais=pais_esperado
    )

    assert artista.nome == nome_esperado
    assert artista.genero == genero_esperado
    assert artista.pais == pais_esperado
    assert artista.id is None

def test_salvamento_correto_artista(app):
    artista = Artista(nome="mac miller", genero="hip hop", pais="EUA")
    db.session.add(artista)
    db.session.commit()

    assert artista.id is not None
    assert artista.id > 0

def test_exclusao_artista_deletar_albuns(app):
    artista = Artista(nome="Kiss of Life")
    db.session.add(artista)
    db.session.commit()

    album = Album(titulo="Born to be XX", ano=2023, artista_id=artista.id)
    db.session.add(album)
    db.session.commit()

    album_id = album.id

    db.session.delete(artista)
    db.session.commit()

    album_banco = db.session.get(Album, album_id)
    assert album_banco is None

def test_salvamento_incorreto_artista(app):
    artista_invalido = Artista(genero="rock", pais="EUA")
    db.session.add(artista_invalido)

    with pytest.raises(IntegrityError):
        db.session.commit()