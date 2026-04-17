from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.usuario import Usuario
from app.schemas.usuario import usuario_schema, usuarios_schema

usuario_bp = Blueprint('usuario', __name__, url_prefix='/usuarios')

@usuario_bp.route('/', methods=['GET'], strict_slashes=False)
def get_usuarios():
    todos_usuarios = Usuario.query.all()
    return jsonify(usuarios_schema.dump(todos_usuarios))

@usuario_bp.route('/<int:id>', methods=['GET'])
def get_usuario(id):
    usuario_id = Usuario.query.get_or_404(id)
    return jsonify(usuario_schema.dump(usuario_id))

@usuario_bp.route('/', methods=['POST'], strict_slashes=False)
def create_usuario():
    json_data = request.get_json()
    try:
        novo_usuario = usuario_schema.load(json_data)
    
        db.session.add(novo_usuario)
        db.session.commit()

        return usuario_schema.dump(novo_usuario), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@usuario_bp.route('/<int:id>', methods=['PUT'])
def edit_usuario(id):
    usuario = Usuario.query.get_or_404(id)

    data = request.get_json()
    usuario.user = data.get('user', usuario.user)
    usuario.email = data.get('email', usuario.email)
    usuario.password = data.get('password', usuario.password)

    db.session.commit()
    return jsonify({
        "usuario": usuario_schema.dump(usuario),
        "message": "Os dados do usuário foram atualizados com sucesso"
    })
    
@usuario_bp.route('/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    nome_usuario = usuario.user

    db.session.delete(usuario)
    db.session.commit()

    return jsonify({
        "message": f"Usuário'{nome_usuario}' e suas avaliações foram deletadas com sucesso"
    })

    