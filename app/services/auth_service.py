from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash
from app.extensions import db
from app.models.usuario import Usuario

class AuthService:
    @staticmethod
    def login(email, password):
        usuario = Usuario.query.filter_by(email=email).first()

        if not usuario or not check_password_hash(usuario.password, password):
            return {"error": "Credenciais inválidas"}, 401
        
        access_token = create_access_token(identity=str(usuario.id))

        return {
            "access_token": access_token,
            "user": {
                "user": usuario.user,
                "email": usuario.email
            }
        }, 200
    
    @staticmethod
    def register(user, email, password):
        if Usuario.query.filter_by(email=email).first():
            return {"status": "error", "message": "Email já registrado"}, 400
        
        novo_usuario = Usuario (
            user = user,
            email = email,
            password = generate_password_hash(password)
        )

        db.session.add(novo_usuario)
        db.session.commit()

        return {
            "status": "success",
            "message": "Usuário registrado com sucesso",
            "user": {
                "user": novo_usuario.user,
                "email": novo_usuario.email
            }
        }, 201