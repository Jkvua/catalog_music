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

        usuarios = [
                {"user": "camila", "password": "password1", "email": "camila@example.com"},
                {"user": "jandira", "password": "password2", "email": "jandira@example.com"},
                {"user": "damiao", "password": "password3", "email": "damiao@example.com"},
                {"user": "carol", "password": "password4", "email": "carol@example.com"},
                {"user": "mariaclara", "password": "password5", "email": "mariaclara@example.com"},
                {"user": "mariaeduarda", "password": "password6", "email": "mariaeduarda@example.com"},
                {"user": "isabel", "password": "password7", "email": "isabel@example.com"},
                {"user": "gabriela", "password": "password8", "email": "gabriela@example.com"},
                {"user": "josevictor", "password": "password9", "email": "josevictor@example.com"},
                {"user": "lina", "password": "password10", "email": "lina@example.com"},
                {"user": "pimenta", "password": "password11", "email": "pimenta@example.com"},
                {"user": "lucia", "password": "password12", "email": "lucia@example.com"},
                {"user": "fernando", "password": "password13", "email": "fernando@example.com"}
            ]
        print(f"Adicionando {len(usuarios)} usuários...")
        sucesso_usuario = 0
        errors_usuarios = 0

        for info in usuarios:
            novo_usuario, status = UsuarioService.criar_usuario(info)

            if status == 201:
                print(f"Sucesso: {info['email']} adicionado.")
                sucesso_usuario +1
            else:
                print(f"Error: {info['email']} não cadastrado. Detalhe: {novo_usuario['error']}")
                errors_usuarios +1
                
    
        artistas = [
                {"nome": "The Beatles", "genero": "Rock", "pais": "Reino Unido"},
                {"nome": "Beyoncé", "genero": "Pop/R&B", "pais": "Estados Unidos"},
                {"nome": "Bob Marley", "genero": "Reggae", "pais": "Jamaica"},
                {"nome": "Taylor Swift", "genero": "Pop/Country", "pais": "Estados Unidos"},
                {"nome": "Queen", "genero": "Rock", "pais": "Reino Unido"},
                {"nome": "Eminem", "genero": "Hip-Hop/Rap", "pais": "Estados Unidos"},
                {"nome": "Adele", "genero": "Pop/Soul", "pais": "Reino Unido"},
                {"nome": "Michael Jackson", "genero": "Pop/Funk", "pais": "Estados Unidos"},
                {"nome": "Coldplay", "genero": "Rock Alternativo", "pais": "Reino Unido"},
                {"nome": "Rihanna", "genero": "Pop/R&B", "pais": "Barbados"},
                {"nome": "AnaVitoria", "genero": "Pop/MPB", "pais": "Brasil"},
                {"nome": "Legião Urbana", "genero": "Rock", "pais": "Brasil"},
                {"nome": "Chico Buarque", "genero": "MPB", "pais": "Brasil"},
                {"nome": "Marisa Monte", "genero": "MPB/Pop", "pais": "Brasil"},
                {"nome": "Gilberto Gil", "genero": "MPB/Reggae", "pais": "Brasil"},
                {"nome": "Elis Regina", "genero": "MPB", "pais": "Brasil"},
                {"nome": "Caetano Veloso", "genero": "MPB/Pop", "pais": "Brasil"},
                {"nome": "Djavan", "genero": "MPB/Jazz", "pais": "Brasil"},
                {"nome": "Zeca Pagodinho", "genero": "Samba/Pagode", "pais": "Brasil"},
                {"nome": "Ivete Sangalo", "genero": "Axé/Pop", "pais": "Brasil"}
            ]
        
        print(f"Adicionando {len(artistas)} artistas...")
        sucesso =  0
        errors = 0

        for info in artistas:
            novo_artista, status = ArtistaService.criar_artista(info)

            if status == 201:
                print(f"Sucesso: {info['nome']} adicionado.")
                sucesso += 1
            else:
                print(f"Erro: {info['nome']} não cadastrado. Detalhes: {novo_artista['error']}")
                errors += 1
        
        print(f"Resumo: {sucesso}, criados, {errors} pulados")
        print("Finalizado")
        

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

        musicas = [
                {"titulo": "Come Together", "duracao": " 4:20", "album": "Abbey Road", "artista": "The Beatles"},
                {"titulo": "Sorry", "duracao": "3:53", "album": "Lemonade", "artista": "Beyoncé"},
                {"titulo": "Is This Love", "duracao": "3:52", "album": "Legend", "artista": "Bob Marley"},
                {"titulo": "Blank Space", "duracao": "3:52", "album": "1989", "artista": "Taylor Swift"},
                {"titulo": "Sweet Lady", "duracao": "4:00"  , "album": "A Night at the Opera", "artista": "Queen"},
                {"titulo": "Kill You", "duracao": "4:25", "album": "The Marshall Mathers LP", "artista": "Eminem"},
                {"titulo": "Hello", "duracao": "4:55", "album": "25", "artista": "Adele"},
                {"titulo": "Thriller", "duracao": "5:58", "album": "Thriller", "artista": "Michael Jackson"},
                {"titulo": "In My Place", "duracao": "3:47", "album": "A Rush of Blood to the Head", "artista": "Coldplay"},
                {"titulo": "Work", "duracao": "3:39", "album": "Anti", "artista": "Rihanna"},
                {"titulo": "Singular", "duracao": "3:35", "album": "AnaVitoria", "artista": "AnaVitoria"},
                {"titulo": "Central do Brasil", "duracao": "1:37", "album": "Dois", "artista": "Legião Urbana"},
                {"titulo": "Vida", "duracao": "3:24", "album": "Vida", "artista": "Chico Buarque"},
                {"titulo": "Ainda Lembro", "duracao": "4:11", "album": "Mais", "artista": "Marisa Monte"},
                {"titulo": "Tempo rei", "duracao": "5:10", "album": "Raça Humana", "artista": "Gilberto Gil"},
                {"titulo": "Como nossos pais", "duracao": "4:22", "album": "Falso Brilhante", "artista": "Elis Regina"},
                {"titulo": "Outro", "duracao": "2:52", "album": "Cê", "artista": "Caetano Veloso"},
                {"titulo": "Oceano", "duracao": "4:56", "album": "Djavan", "artista": "Djavan"},
                {"titulo": "Tá Ruim, mas Tá Bom", "duracao": "5:00", "album": "Deixa a vida me levar", "artista": "Zeca Pagodinho"},
                {"titulo": "Tá Tudo Bem", "duracao": "3:48", "album": "Ivete Sangalo", "artista": "Ivete Sangalo"},
            ]
        
        print(f"Adicionando {len(musicas)} musicas...")
        sucesso =  0
        errors = 0

        for info in musicas:
            nova_musica, status = MusicaService.criar_musica(info)

            if status == 201:
                print(f"Sucesso: {info['titulo']} adicionado.")
                sucesso += 1
            else:
                print(f"Erro: {info['titulo']} não cadastrado. Detalhes: {nova_musica['error']}")
                errors += 1
        
        print(f"Resumo: {sucesso}, criados, {errors} pulados")
        print("Finalizado")

        avaliacoes = [
                {"nota": 2, "comentario": "Não faz meu estilo, o estrumenal é diferente.", "data_escuta": "2026-04-22", "album": "Abbey Road", "usuario_email": "camila@example.com"},
                {"nota": 2, "comentario": "Não é ruim, mas não é muito bom", "data_escuta": "2026-04-22", "album": "Lemonade", "usuario_email": "mariaeduarda@example.com"},
                {"nota": 5, "comentario": "Muito bom, ele nunca fez músicas ruins", "data_escuta": "2026-04-22", "album": "Legend", "usuario_email": "carol@example.com"},
                {"nota": 4, "comentario": "Muito bom, um dos meus albuns favoritos dela!", "data_escuta": "2026-04-22", "album": "1989", "usuario_email": "isabel@example.com"},
                {"nota": 5, "comentario": "Ótimo instrumental. Queen é muito bom"  , "data_escuta": "2026-04-22", "album": "A Night at the Opera", "usuario_email": "jandira@example.com"},
                {"nota": 4, "comentario": "O Eminem é uma baita rapper", "data_escuta": "2026-04-22", "album": "The Marshall Mathers LP", "usuario_email": "josevictor@example.com"},
                {"nota": 3, "comentario": "Gosto da voz dela, mas não escutaria sempre", "data_escuta": "2026-04-22", "album": "25", "usuario_email": "mariaeduarda@example.com"},
                {"nota": 5, "comentario": "O rei do pop. INCRIVEL", "data_escuta": "2026-04-22", "album": "Thriller", "usuario_email": "jandira@example.com"},
                {"nota": 3, "comentario": "Lindo", "data_escuta": "2026-04-22", "album": "A Rush of Blood to the Head", "usuario_email": "josevictor@example.com"},
                {"nota": 2, "comentario": "Lembra 2015. É um album legal", "data_escuta": "2026-04-22", "album": "Anti", "usuario_email": "mariaeduarda@example.com"},
                {"nota": 5, "comentario": "Lindo, traz conforto", "data_escuta": "2026-04-22", "album": "AnaVitoria", "usuario_email": "camila@example.com"},
                {"nota": 4, "comentario": "Grandes clássicos presentes!", "data_escuta": "2026-04-22", "album": "Dois", "usuario_email": "pimenta@example.com"},
                {"nota": 3, "comentario": "Parece que sempre aprendemos algo ao longo das músicas", "data_escuta": "2026-04-22", "album": "Vida", "usuario_email": "isabel@example.com"},
                {"nota": 4, "comentario": "Não existe uma obra ruim dela!!", "data_escuta": "2026-04-22", "album": "Mais", "usuario_email": "camila@example.com"},
                {"nota": 3, "comentario": "O fato dele ser instrumentista, faz tudo ficar melhor", "data_escuta": "2026-04-22", "album": "Raça Humana", "usuario_email": "pimenta@example.com"},
                {"nota": 3, "comentario": "Não sou uma grande fã dela, mas ótimo álbum", "data_escuta": "2026-04-22", "album": "Falso Brilhante", "usuario_email": "damiao@example.com"},
                {"nota": 1, "comentario": "Não gostei por mais que o instrumental seje interessante", "data_escuta": "2026-04-22", "album": "Cê", "usuario_email": "pimenta@example.com"},
                {"nota": 5, "comentario": "Lindo, simplismente magnífico.", "data_escuta": "2026-04-22", "album": "Djavan", "usuario_email": "camila@example.com"},
                {"nota": 5, "comentario": "Muto bom!", "data_escuta": "2026-04-22", "album": "Deixa a vida me levar", "usuario_email": "damiao@example.com"},
                {"nota": 1, "comentario": "Não gostei", "data_escuta": "2026-04-22", "album": "Ivete Sangalo", "usuario_email": "damiao@example.com"},
            ]
        
        print(f"Adicionando {len(avaliacoes)} avaliacoes...")
        sucesso =  0
        errors = 0

        for info in avaliacoes:
            nova_avaliacao, status = AvaliacaoService.criar_avaliacao(info)

            if status == 201:
                print(f"Sucesso: avaliação de {info['album']} adicionada.")
                sucesso += 1
            else:
                print(f"Erro: avaliação do album {info['album']} não cadastrada. Detalhes: {nova_avaliacao['error']}")
                errors += 1
        
        print(f"Resumo: {sucesso}, criados, {errors} pulados")
        print("Finalizado")


if __name__ == "__main__":
    create_seed_data()