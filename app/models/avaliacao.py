from app.extensions import db
class Avaliacao(db.Model):
    __tablename__ = "avaliacao"

    __table_args__ = (db.UniqueConstraint('usuario_id', 'album_id', name='unique_usuario_album'),)

    id = db.Column(db.Integer, primary_key=True)
    nota = db.Column(db.Float, nullable=False)
    comentario = db.Column(db.Text)
    data_escuta = db.Column(db.Date)

    album_id = db.Column(db.Integer, db.ForeignKey("albuns.id", ondelete="CASCADE"), nullable=False)
    album = db.relationship("Album", back_populates="avaliacoes")

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    usuario = db.relationship("Usuario", back_populates="avaliacoes")
    