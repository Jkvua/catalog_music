from app.extensions import ma
from app.models.album import Album
from marshmallow import fields, validate
from app.extensions import db

class AlbumSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Album
        load_instance = True
        include_fk = False
        sqla_session = db.session

    titulo = fields.String(required=True, validate=validate.Length(min=1, max=200))
    ano_lancamento = fields.Integer(required=True, validate=validate.Range(min=1900, max=2100))
    
    musicas = fields.Nested('MusicaSchema', many=True)
    avaliacao = fields.Nested('AvaliacaoSchema', many=True, exclude=('album_id',))

album_schema = AlbumSchema()
albums_schema = AlbumSchema(many=True)  