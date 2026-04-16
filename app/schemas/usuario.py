from app.extensions import ma, db
from app.models.usuario import Usuario
from marshmallow import fields, validate

class UsuarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        sqla_session = db.session
        load_instance = True
        load_only = ("password",)

    nome = fields.String(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True, validate=validate.Length(max=100))

    avaliacoes = fields.Nested("AvaliacaoSchema", many=True, only=('id', 'nota', 'comentario', 'album')) 

usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)