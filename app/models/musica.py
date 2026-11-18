from app.extensions import db

class Musica(db.Model):
    __tablename__ = "musica"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    duracao = db.Column(db.String(20), nullable=False)
    
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey("albuns.id", ondelete="CASCADE"), nullable=False)
    
    usuario = db.relationship("Usuario", back_populates="musicas")
    album = db.relationship("Album", back_populates="musicas")