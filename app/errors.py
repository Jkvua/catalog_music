from flask import jsonify
from werkzeug.exceptions import HTTPException
from marshmallow import ValidationError
import traceback

def register_errors(app):

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        response = {
            "status": "error",
            "code": e.code,
            "name": e.name,
            "description": e.description
        }
        return jsonify(response), e.code
    
    @app.errorhandler(ValidationError)
    def handle_marshmallow_validation(e):
        return jsonify({
            "status": "invalid_data",
            "message": "Dados enviados são inválidos", 
            "errors": e.messages      
        }), 400
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        print("Erro inesperado", e)
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": "Ocorreu um erro inesperado"
        }), 500