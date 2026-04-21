from app import create_app
from app.extensions import db
from app.services.album import AlbumService
from app.services.artista import ArtistaService
from app.services.musica import MusicaService
from app.services.usuario import UsuarioService
from app.services.avaliacoes import AvaliacaoService

def create_seed_data():
    app = create_app()
    with app.app_context():
        # print("Limpando banco de dados...")

        # db.drop_all()
        db.create_all()

        # usuarios = [
        #         {"user": "camila", "password": "password1", "email": "camila@example.com"},
        #         {"user": "jandira", "password": "password2", "email": "jandira@example.com"},
        #         {"user": "damiao", "password": "password3", "email": "damiao@example.com"},
        #         {"user": "carol", "password": "password4", "email": "carol@example.com"},
        #         {"user": "mariaclara", "password": "password5", "email": "mariaclara@example.com"},
        #         {"user": "mariaeduarda", "password": "password6", "email": "mariaeduarda@example.com"},
        #         {"user": "isabel", "password": "password7", "email": "isabel@example.com"},
        #         {"user": "gabriela", "password": "password8", "email": "gabriela@example.com"},
        #         {"user": "josevictor", "password": "password9", "email": "josevictor@example.com"},
        #         {"user": "lina", "password": "password10", "email": "lina@example.com"},
        #         {"user": "pimenta", "password": "password11", "email": "pimenta@example.com"},
        #         {"user": "lucia", "password": "password12", "email": "lucia@example.com"},
        #         {"user": "fernando", "password": "password13", "email": "fernando@example.com"}
        #     ]
        # print(f"Adicionando {len(usuarios)} usuários...")
        # sucesso_usuario = 0
        # errors_usuarios = 0

        # for info in usuarios:
        #     novo_usuario, status = UsuarioService.criar_usuario(info)

        #     if status == 201:
        #         print(f"Sucesso: {info['email']} adicionado.")
        #         sucesso_usuario +1
        #     else:
        #         print(f"Error: {info['email']} não cadastrado. Detalhe: {novo_usuario['error']}")
    
        # artistas = [
        #         {"nome": "The Beatles", "genero": "Rock", "pais": "Reino Unido"},
        #         {"nome": "Beyoncé", "genero": "Pop/R&B", "pais": "Estados Unidos"},
        #         {"nome": "Bob Marley", "genero": "Reggae", "pais": "Jamaica"},
        #         {"nome": "Taylor Swift", "genero": "Pop/Country", "pais": "Estados Unidos"},
        #         {"nome": "Queen", "genero": "Rock", "pais": "Reino Unido"},
        #         {"nome": "Eminem", "genero": "Hip-Hop/Rap", "pais": "Estados Unidos"},
        #         {"nome": "Adele", "genero": "Pop/Soul", "pais": "Reino Unido"},
        #         {"nome": "Michael Jackson", "genero": "Pop/Funk", "pais": "Estados Unidos"},
        #         {"nome": "Coldplay", "genero": "Rock Alternativo", "pais": "Reino Unido"},
        #         {"nome": "Rihanna", "genero": "Pop/R&B", "pais": "Barbados"},
        #         {"nome": "AnaVitoria", "genero": "Pop/MPB", "pais": "Brasil"},
        #         {"nome": "Legião Urbana", "genero": "Rock", "pais": "Brasil"},
        #         {"nome": "Chico Buarque", "genero": "MPB", "pais": "Brasil"},
        #         {"nome": "Marisa Monte", "genero": "MPB/Pop", "pais": "Brasil"},
        #         {"nome": "Gilberto Gil", "genero": "MPB/Reggae", "pais": "Brasil"},
        #         {"nome": "Elis Regina", "genero": "MPB", "pais": "Brasil"},
        #         {"nome": "Caetano Veloso", "genero": "MPB/Pop", "pais": "Brasil"},
        #         {"nome": "Djavan", "genero": "MPB/Jazz", "pais": "Brasil"},
        #         {"nome": "Zeca Pagodinho", "genero": "Samba/Pagode", "pais": "Brasil"},
        #         {"nome": "Ivete Sangalo", "genero": "Axé/Pop", "pais": "Brasil"}
        #     ]
        
        # print(f"Adicionando {len(artistas)} artistas...")
        # sucesso =  0
        # errors = 0

        # for info in artistas:
        #     novo_artista, status = ArtistaService.criar_artista(info)

        #     if status == 201:
        #         print(f"Sucesso: {info['nome']} adicionado.")
        #         sucesso += 1
        #     else:
        #         print(f"Erro: {info['nome']} não cadastrado. Detalhes: {novo_artista['error']}")
                #   errors += 1
        
        # print(f"Resumo: {sucesso}, criados, {errors} pulados")
        # print("Finalizado")
        

        albuns = [
                {"titulo": "Abbey Road", "ano": 1969, "artista": "The Beatles"},
                {"titulo": "Lemonade", "ano": 2016, "artista": "Beyoncé"},
                {"titulo": "Legend", "ano": 1984, "artista": "Bob Marley"},
                {"titulo": "1989", "ano": 2014, "artista": "Taylor Swift"},
                {"titulo": "A Night at the Opera", "ano": 1975, "artista": "Queen"},
                {"titulo": "The Marshall Mathers LP", "ano": 2000, "artista": "Eminem"},
                {"titulo": "25", "ano": 2015, "artista": "Adele"},
                {"titulo": "Thriller", "ano": 1982, "artista": "Michael Jackson"},
                {"titulo": "A Rush of Blood to the Head", "ano": 2002, "artista": "Coldplay"},
                {"titulo": "Anti", "ano": 2016, "artista": "Rihanna"},
                {"titulo": "AnaVitoria", "ano": 2016, "artista": "AnaVitoria"},
                {"titulo": "Dois", "ano": 1986, "artista": "Legião Urbana"},
                {"titulo": "Vida", "ano": 1980, "artista": "Chico Buarque "},
                {"titulo": "Mais", "ano": 1991, "artista": "Marisa Monte"},
                {"titulo": "Raça Humana", "ano": 1984, "artista": "Gilberto Gil"},
                {"titulo": "Falso Brilhante", "ano": 1976, "artista": "Elis Regina"},
                {"titulo": "Cê", "ano": 2006, "artista": "Caetano Veloso"},
                {"titulo": "Djavan", "ano": 1986, "artista": "Djavan"},
                {"titulo": "Deixa a vida me levar", "ano": 2002, "artista": "Zeca Pagodinho"},
                {"titulo": "Ivete Sangalo", "ano": 1999, "artista": "Ivete Sangalo"},
            ]
        
        print(f"Adicionando {len(albuns)} albuns...")
        sucesso =  0
        errors = 0

        for info in albuns:
            novo_album, status = AlbumService.criar_album(info)

            if status == 201:
                print(f"Sucesso: {info['titulo']} adicionado.")
                sucesso += 1
            else:
                print(f"Erro: {info['titulo']} não cadastrado. Detalhes: {novo_album['error']}")
                errors += 1
        
        print(f"Resumo: {sucesso}, criados, {errors} pulados")
        print("Finalizado")





if __name__ == "__main__":
    create_seed_data()