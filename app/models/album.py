from app.extensions import db


class Album(db.Model):
    __tablename__ = "albuns"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    ano = db.Column(db.Integer)
    artista_id = db.Column(db.Integer, db.ForeignKey('artistas.id'), nullable=False)
    
    artista = db.relationship('Artista', back_populates='albuns')
    musica = db.relationship('Musica', back_populates='album', cascade="all, delete-orphan")