from app import create_app

application = create_app()

print("A URL do banco de dados carregada foi:", application.config['SQLALCHEMY_DATABASE_URI'])

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000, debug=True)
