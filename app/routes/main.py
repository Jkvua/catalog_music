from flask import Blueprint, request, jsonify, current_app

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    rotas = []
    for rule in current_app.url_map.iter_rules():
       if "static" not in rule.endpoint:
           rotas.append({
               "endpoint": rule.endpoint,
               "methods": list(rule.methods),
               "url": str(rule)
           })
    return jsonify({"message": "Bem-vindo ao Catalog Music API!",
                    "rotas disponiveis": rotas
                })