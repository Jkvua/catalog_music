from app.extensions import db

class Artista(db.Model):
    __tablename__ = "artistas"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    genero = db.Column(db.String(50))
    pais = db.Column(db.String(50))

    albuns = db.relationship('Album', back_populates='artista', cascade="all, delete-orphan")
    musicas = db.relationship('Musica', back_populates='artista')