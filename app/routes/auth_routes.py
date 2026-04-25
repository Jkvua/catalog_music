from flask import Blueprint, request, jsonify
from app.services.auth_serivce import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    email = dados.get('email')
    senha = dados.get('senha')

    resultado, status = AuthService.login(email, senha)
    return jsonify(resultado), status