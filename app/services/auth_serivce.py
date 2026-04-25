from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from app.models.usuario import Usuario

class AuthService:
    @staticmethod
    def login(email, senha):
        usuario = Usuario.query.filter_by(email=email).first()

        if not usuario or not check_password_hash(usuario.senha, senha):
            return {"error": "Credenciais inválidas"}, 401
        
        access_token = create_access_token(identity=str(usuario.id))

        return {
            "access_token": access_token,
            "user": {
                "username": usuario.username,
                "email": usuario.email
            }
        }, 200