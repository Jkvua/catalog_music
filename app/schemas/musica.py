from app.extensions import ma, db
from app.models.musica import Musica
from app.schemas.album import AlbumSchema
from app.schemas.artista import ArtistaSchema
from marshmallow import fields, validate
class MusicaInputSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Musica
        load_instance = True
        include_fk = True
        sqla_session = db.session
        
    titulo = fields.String(required=True, validate=validate.Length(min=1, max=200))
    duracao = fields.String(required=True, validate=validate.Length(min=1, max=30))

    def validate_duracao(self, value):
        try:
            minutos, segundos = value.split(':')
            minutos = int(minutos)
            segundos = int(segundos)

            if minutos < 0 or segundos < 0 or segundos >= 60:
                raise validate.ValidationError("Formato de duração da música inválido. Use MM:SS (ex.: 03:45)")
        except (ValueError, AttributeError):
            raise validate.ValidationError("A duração da música está em um formato inválido, use MM:SS")

musica_schema = MusicaInputSchema()
musicas_schema = MusicaInputSchema(many=True)

class MusicaOutputSchema(MusicaInputSchema):
    class Meta(MusicaInputSchema.Meta):
        model = Musica
        load_instance = True
        include_fk = False
        sqla_session = db.session
    
    album = fields.Nested(AlbumSchema, only=('id', 'titulo')) #-- para mostrar título do álbum
    artista = fields.Nested(ArtistaSchema, only=('id', 'nome')) #-- para mostrar nome do artista

musica_output_schema = MusicaOutputSchema()
musicas_output_schema = MusicaOutputSchema(many=True)
