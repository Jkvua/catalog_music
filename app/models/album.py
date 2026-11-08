from app.extensions import db


class Album(db.Model):
    __tablename__ = "albuns"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    ano = db.Column(db.Integer)
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete="CASCADE"), nullable=True)
    artista_id = db.Column(db.Integer, db.ForeignKey('artistas.id', ondelete="CASCADE"), nullable=False)
    artista = db.relationship('Artista', back_populates='albuns')
    
    musicas = db.relationship('Musica', back_populates='album', cascade="all, delete-orphan")
    avaliacoes = db.relationship("Avaliacao", back_populates="album", cascade="all, delete-orphan")