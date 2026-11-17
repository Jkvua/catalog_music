from app.extensions import db
from sqlalchemy.orm import backref

class Artista(db.Model):
    __tablename__ = "artistas"

    __table_args__ = (
        db.Index(
            'idx_usuario_artista_nome',
            'usuario_id',
            'nome',
            unique=True
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    genero = db.Column(db.String(50))
    pais = db.Column(db.String(50))

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete="CASCADE"), nullable=False)
    usuario = db.relationship("Usuario", back_populates="artistas")
    albuns = db.relationship('Album', back_populates='artista', cascade="all, delete-orphan")
    
