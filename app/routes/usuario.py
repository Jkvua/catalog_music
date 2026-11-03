from flask import Blueprint, request, jsonify
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.usuario import Usuario
from app.services.usuario import UsuarioService
from app.schemas.usuario import usuario_schema, usuarios_schema

usuario_bp = Blueprint('usuario', __name__, url_prefix='/usuarios')

# -- usuário comum -- #
@usuario_bp.route('/me', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_me():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get_or_404(usuario_id)
    return jsonify(usuario_schema.dump(usuario))

@usuario_bp.route('/', methods=['POST'], strict_slashes=False)
def create_usuario():
    data = request.get_json()

    usuario, status = UsuarioService.criar_usuario(data)
    if status == 400:
        return jsonify(usuario), status

    return jsonify({
        "usuario": usuario_schema.dump(usuario),
        "message": "O usuário foi criado com sucesso"
    }), status
    
@usuario_bp.route('/me', methods=['PUT'])
@jwt_required()
def edit_usuario():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get_or_404(usuario_id)

    data = request.get_json()
    usuario.user = data.get('user', usuario.user)
    usuario.email = data.get('email', usuario.email)
    usuario.password = data.get('password', usuario.password)

    db.session.commit()

    return jsonify({
        "usuario": usuario_schema.dump(usuario),
        "message": "Os dados do usuário foram atualizados com sucesso"
    })  

@usuario_bp.route('/me', methods=['DELETE'])
@jwt_required()
def delete_usuario():
    usuario_id = get_jwt_identity()
    usuario = Usuario.query.get_or_404(usuario_id)

    db.session.delete(usuario)
    db.session.commit()

    return {"message": "usuario e todos os seus dados foram excluídos com sucesso"}

# -- usuário admin -- #

@usuario_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_all_usuarios():
    if not UsuarioService.is_admin(get_jwt_identity()):
        return jsonify({"error": "Acesso negado"}), 403

    todos_usuarios = Usuario.query.all()
    return jsonify(usuarios_schema.dump(todos_usuarios))

@usuario_bp.route('/<int:id>', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_usuarios(id):
    if not UsuarioService.is_admin(get_jwt_identity()):
        return jsonify({"error": "Acesso negado"}), 403

    usuario = Usuario.query.get_or_404(id)
    return jsonify(usuario_schema.dump(usuario))

@usuario_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def edit_usuarios(id):
    if not UsuarioService.is_admin(get_jwt_identity()):
        return jsonify({"error": "Acesso negado"}), 403

    data = request.get_json()
    usuario = Usuario.query.get_or_404(id)
    usuario.user = data.get('user', usuario.user)
    usuario.email = data.get('email', usuario.email)
    usuario.password = data.get('password', usuario.password)

    db.session.commit()

    return jsonify({
        "usuario": usuario_schema.dump(usuario),
        "message": "Os dados do usuário foram atualizados com sucesso"
    })

@usuario_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_usuarios(id):
    if not UsuarioService.is_admin(get_jwt_identity()):
        return jsonify({"error": "Acesso negado"}), 403
    
    resposta, status = UsuarioService.deletar_usuario(id)

    return jsonify({
       resposta["message"]: "usuario e todos os seus dados foram excluídos com sucesso"
    }), status

    