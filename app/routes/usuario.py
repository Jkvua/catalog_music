from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.usuario import Usuario

usuario_bp = Blueprint('usuario', __name__)

@usuario_bp.route('/usuarios', methods=['GET'], strict_slashes=False)
def get_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([{"id": usuario.id, "user": usuario.user} for usuario in usuarios])

# @usuario_bp.route('/usuarios/<int:id>', methods=['GET'])
# def get_usuario(id):
#     usuario = Usuario.query.get_or_404(id)
#     return jsonify({"id": usuario.id, "user": usuario.user})

@usuario_bp.route('/usuarios/', methods=['POST'], strict_slashes=False)
def create_usuario():
    data = request.get_json()
    if not data or not "user" in data or not "password" in data:
        return jsonify({"error": "Dados inválidos"}), 400
    
    novo = Usuario(user=data["user"],
                   password=data["password"]
        )
    
    db.session.add(novo)
    db.session.commit()

    return jsonify({
        "id": novo.id, 
        "user": novo.user
    }), 201