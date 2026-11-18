import pytest
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models.artista import Artista
from app.models.album import Album
from app.models.usuario import Usuario

def test_salvamento_correto_artista(app):
    with app.app_context():
        usuario = Usuario(
            user="Camila",
            email="camila@exemplo.com",
            password="123456"
        )

        db.session.add(usuario)
        db.session.commit()

        artista = Artista(
            nome="Mac Miller",
            genero="Hip Hop",
            pais="EUA",
            usuario_id=usuario.id
        )

        db.session.add(artista)
        db.session.commit()

        assert artista.id is not None
        assert artista.id > 0
        assert artista.usuario_id == usuario.id

def test_exclusao_artista_deletar_albuns(app):
    with app.app_context():
        usuario = Usuario(
            user="Camila",
            email="camila@exemplo.com",
            password="123456"
        )

        db.session.add(usuario)
        db.session.commit()

        artista = Artista(
            nome="Kiss of Life",
            usuario_id=usuario.id
        )

        db.session.add(artista)
        db.session.commit()

        album = Album(
            titulo="Born to be XX",
            ano=2023,
            artista_id=artista.id,
            usuario_id=usuario.id
        )

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