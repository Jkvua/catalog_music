from app.extensions import db

class Musica(db.Model):
    __tablename__ = "musica"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    duracao = db.Column(db.String(20), nullable=False)
    #faixa = db.Column(db.Integer)

    album_id = db.Column(db.Integer, db.ForeignKey("albuns.id"))
    album = db.relationship("Album", back_populates="musicas")

    artista_id = db.Column(db.Integer, db.ForeignKey("artistas.id"))
    artista = db.relationship("Artista", back_populates="musicas")
    