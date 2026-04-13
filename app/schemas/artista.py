from app.extensions import ma
from app.models.artista import Artista
from marshmallow import fields, validate
from app.extensions import db

class ArtistaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Artista
        load_instance = True
        sqla_session = db.session #cria pasta so para validacao

    album = fields.Nested('AlbumSchema', many=True)
    nome = fields.String(required=True, validate=validate.Length(min=1, max=200))
    genero = fields.String(required=True, dump_default="Desconhecido")
    pais = fields.String(required=True, validate=validate.Length(min=1, max=100))

artista_schema = ArtistaSchema()
artistas_schema = ArtistaSchema(many=True)
