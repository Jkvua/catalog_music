from flask import Blueprint, request, jsonify
from app.extensions import db
from flask_jwt_extended import jwt_required
from app.models.usuario import Usuario
from app.services.usuario import UsuarioService
from app.schemas.usuario import usuario_schema, usuarios_schema

usuario_bp = Blueprint('usuario', __name__, url_prefix='/usuarios')

@usuario_bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_usuarios():
    todos_usuarios = Usuario.query.all()
    return jsonify(usuarios_schema.dump(todos_usuarios))

@usuario_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_usuario(id):
    usuario_id = Usuario.query.get_or_404(id)
    return jsonify(usuario_schema.dump(usuario_id))

@usuario_bp.route('/', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_usuario():
    data = request.get_json()

    usuario, status = UsuarioService.criar_usuario(data)
    if status == 400:
        return jsonify(usuario), status

    return jsonify({
        "usuario": usuario_schema.dump(usuario),
        "message": "O usuário foi criado com sucesso"
    }), status
    
@usuario_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def edit_usuario(id):
    data = request.get_json()

    usurio, status = Usuario.query.get_or_404(id)
    if status == 404:
        return jsonify(usurio), status
    
    return jsonify({
        "usuario": usuario_schema.dump(usurio),
        "message": "Os dados do usuário foram atualizados com sucesso"
    }), status
    
@usuario_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_usuario(id):
    resposta, status = UsuarioService.delete_usuario(id)

    return jsonify({
       resposta["message"]: "usuario e todos os seus dados foram excluídos com sucesso"
    }), status

    