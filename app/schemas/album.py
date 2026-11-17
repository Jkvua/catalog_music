from app.extensions import ma, db
from app.models.album import Album
from marshmallow import fields


class AlbumSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Album
        load_instance = True
        include_fk = False
        sqla_session = db.session

    titulo = fields.String()
    ano = fields.Integer(allow_none=True)
    artista = fields.Nested('ArtistaSchema', only=('id', 'nome'))
    musicas = fields.Nested('MusicaOutputSchema', many=True)
    avaliacoes = fields.Nested('AvaliacaoSchema', many=True, only=('id', 'nota', 'comentario', 'data_escuta'))

    usuario_id = fields.Integer()


album_schema = AlbumSchema()
albums_schema = AlbumSchema(many=True)