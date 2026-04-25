from flask import Blueprint, request, jsonify
from app.services.auth_serivce import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=["POST"])
def login():
    dados = request.get_json()
    email = dados.get('email')
    password = dados.get('password')

    resultado, status = AuthService.login(email, password)
    return jsonify(resultado), status

@auth_bp.route('/register', methods=["POST"])
def register():
    data = request.get_json()
    return AuthService.register(data.get("user"), data.get("email"), data.get("password"))