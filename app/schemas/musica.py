from app.extensions import ma, db
from app.models.musica import Musica
from marshmallow import fields


class MusicaInputSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Musica
        load_instance = True
        include_fk = True
        sqla_session = db.session

    titulo = fields.String()
    duracao = fields.String()


musica_schema = MusicaInputSchema()
musicas_schema = MusicaInputSchema(many=True)


class MusicaOutputSchema(MusicaInputSchema):
    class Meta(MusicaInputSchema.Meta):
        include_fk = False

    album = fields.Nested(
        'AlbumSchema',
        only=('id', 'titulo')
    )

    artista = fields.Nested(
        'ArtistaSchema',
        only=('id', 'nome'),
        attribute='album.artista'
    )

    usuario_id = fields.Integer()


musica_output_schema = MusicaOutputSchema()
musicas_output_schema = MusicaOutputSchema(many=True)