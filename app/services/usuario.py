from app.models.usuario import Usuario
from app.extensions import db
from werkzeug.security import generate_password_hash
import re

class UsuarioService:
    @staticmethod

    def validar_email(email):
        regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
        return re.search(regex, email)
    
    def criar_usuario(dados):
        user = dados.get('user')
        email = dados.get('email')
        full_password = dados.get('password')

        if not user or not email or not full_password:
            return {"error": "Os campos 'user', 'email' e 'password' são obrigatórios"}, 400
        if not UsuarioService.validar_email(email):
            return {"error": "O email fornecido é inválido"}, 400

        existente = Usuario.query.filter_by(email=email).first()
        if existente:
            return {"error": f"O email {email} já está em uso"}, 400
        
        existente_user = Usuario.query.filter_by(user=user).first()
        if existente_user:
            return {"error": f"O nome de usuário {user} já está em uso"}, 400
        
        password_hash = generate_password_hash(full_password)
        
        try:
            novo_usuario = Usuario(
                user=user.strip(),
                email=email.strip(),
                password=password_hash
            )

            db.session.add(novo_usuario)
            db.session.commit()
            
            return novo_usuario, 201
        
        except Exception as e:
            db.session.rollback()
            return {"error": "Ocorreu um erro ao criar o usuário"}, 500
    
    def editar_usuario(id, dados):
        usuario = Usuario.query.get_or_404(id)
        if not usuario:
            return {"error": f"Usuário não encontrado"}, 404

        if "user"  in dados:
            usuario.user = dados["user"].strip()

        if "email" in dados:
            novo_email = dados["email"].strip()

            if not UsuarioService.validar_email(novo_email):
                return {"error": "O email fornecido é inválido"}, 400
            if Usuario.query.filter(Usuario.email == novo_email, Usuario.id != id).first():
                return {"error": f"O email {novo_email} já está em uso por outro usuário"}, 400
            usuario.email = novo_email

        if "password" in dados:
            usuario.password = generate_password_hash(dados["password"])
        
        db.session.commit()
        return usuario, 200
    
    @staticmethod
    def delete_usuario(id):
        usuario = Usuario.query.get_or_404(id)

        db.session.delete(usuario)
        db.session.commit()
        return {"message": f"Usuário {usuario.user} e todos os seus dados foram excluídos com sucesso"}, 200