from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=["POST"])
@auth_bp.route('/login', methods=["POST"])
def login():
    dados = request.get_json()

    if not isinstance(dados, dict):
        return jsonify({"error": "O corpo da requisição deve ser um objeto JSON"}), 400

    email = dados.get('email')
    password = dados.get('password')

    resultado, status = AuthService.login(email, password)
    return jsonify(resultado), status

@auth_bp.route('/register', methods=["POST"])
def register():
    dados = request.get_json()

    if not isinstance(dados, dict):
        return jsonify({"error": "O corpo da requisição deve ser um objeto JSON"}), 400

    user = dados.get('user')
    email = dados.get('email')
    password = dados.get('password')

    resultado, status = AuthService.register(user, email, password)
    return jsonify(resultado), status