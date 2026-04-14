from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.usuario import Usuario
from app.schemas.usuario import usuario_schema, usuarios_schema

usuario_bp = Blueprint('usuario', __name__)

@usuario_bp.route('/usuarios', methods=['GET'], strict_slashes=False)
def get_usuarios():
    todos_usuarios = Usuario.query.all()
    return jsonify(usuarios_schema.dump(todos_usuarios))

@usuario_bp.route('/usuarios/<int:id>', methods=['GET'])
def get_usuario(id):
    usuario_id = Usuario.query.get_or_404(id)
    return jsonify(usuario_schema.dump(usuario_id))

@usuario_bp.route('/usuarios/', methods=['POST'], strict_slashes=False)
def create_usuario():
    json_data = request.get_json()
    try:
        novo_usuario = usuario_schema.load(json_data)
    
        db.session.add(novo_usuario)
        db.session.commit()

        return usuario_schema.dump(novo_usuario), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    