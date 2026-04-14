from app.extensions import ma, db
from app.models.avaliacao import Avaliacao
from marshmallow import fields, validate

class AvaliacaoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Avaliacao
        load_instance = True
        sqla_session = db.session
        include_fk = True
     
    nota = fields.Integer(required=True, validate=validate.Range(min=1, max=5))
    comentario = fields.String(validate=validate.Length(max=500))
    #usuario = fields.Nested('UsuarioSchema', exclude=('avaliacao',)) -- mostrar quem avaliou?

avaliacao_schema = AvaliacaoSchema()
avaliacoes_schema = AvaliacaoSchema(many=True)