from app.extensions import ma
from app.models.musica import Musica
from marshmallow import fields, validate
from app.extensions import db

class MusicaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Musica
        load_instance = True
        include_fk = True
        sqla_session = db.session
        
    titulo = fields.String(required=True, validate=validate.Length(min=1, max=200))
    duracao = fields.Integer(required=True, validate=validate.Range(min=1))

musica_schema = MusicaSchema()
musicas_schema = MusicaSchema(many=True)