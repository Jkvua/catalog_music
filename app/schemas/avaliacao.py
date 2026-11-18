from app.extensions import ma, db
from app.models.avaliacao import Avaliacao
from marshmallow import fields


class AvaliacaoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Avaliacao
        load_instance = True
        sqla_session = db.session
        include_fk = True

    id = fields.Integer()
    nota = fields.Integer()
    comentario = fields.String()
    data_escuta = fields.Date()

    usuario = fields.Nested("UsuarioSchema", only=('id', 'user', 'email'))
    album = fields.Nested("AlbumSchema", only=('id', 'titulo', 'musicas', 'artista', 'ano'))

avaliacao_schema = AvaliacaoSchema()
avaliacoes_schema = AvaliacaoSchema(many=True)