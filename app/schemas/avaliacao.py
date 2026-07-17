from app.extensions import ma, db
from app.models.avaliacao import Avaliacao
from app.schemas.album import AlbumSchema
from marshmallow import fields, validate

class AvaliacaoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Avaliacao
        load_instance = True
        sqla_session = db.session
        include_fk = True
     
    id = fields.Integer() 
    nota = fields.Integer(required=True, validate=validate.Range(min=1, max=5))
    comentario = fields.String(validate=validate.Length(max=500))
    data_escuta = fields.Date()
    
    usuario = fields.Nested("UsuarioSchema", only=('id', 'user', 'email'))
    album = fields.Nested(AlbumSchema, only=['id', 'titulo', 'musicas', 'artista', 'ano_lancamento'])

avaliacao_schema = AvaliacaoSchema()    
avaliacoes_schema = AvaliacaoSchema(many=True)