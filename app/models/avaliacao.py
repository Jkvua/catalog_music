from app.extensions import db
class Avaliacao(db.Model):
    __tablename__ = "avaliacao"

    id = db.Column(db.Integer, primary_key=True)
    nota = db.Column(db.Float, nullable=False)
    comentario = db.Column(db.Text)
    data_escuta = db.Column(db.Date)

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    album_id = db.Column(db.Integer, db.ForeignKey("albuns.id"))

    usuario = db.relationship("Usuario", back_populates="avaliacoes")
    album = db.relationship("Album", back_populates="avaliacoes")