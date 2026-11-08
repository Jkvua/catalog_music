import os
import pytest
import requests
import time

BASE_URL = os.getenv("API_URL", "http://localhost:5000")

def test_conflito_email_duplicado():
    "Teste de registar dois usuários com o mesmo email"
    sufixo = str(int(time.time()))
    email = f"jandiragomes{sufixo}@gmail.com"

    res_1 = requests.post(f"{BASE_URL}/auth/register", json={"user": "Jandira", "email": email, "password": "jandira2897"})
    assert res_1.status_code == 201

    res_2 = requests.post(f"{BASE_URL}/auth/register", json={"user": "Jana", "email": email, "password": "janapereira234"})
    assert res_2.status_code in [400, 409], f"Deveria ser bloqueado o email duplicado. Status: {res_2.status_code}"

def test_chave_estrangeira_invalida():
    """Tenta atrelar um dado ao ID inexistente"""
    sufixo = str(int(time.time()))

    requests.post(f"{BASE_URL}/auth/register", json={"user": f"Maicon{sufixo}", "email": f"maiconsilva{sufixo}@gmail.com", "password": "silvamaicon21"})
    res_login = requests.post(f"{BASE_URL}/auth/login", json={"email": f"maiconsilva{sufixo}@gmail.com", "password": "silvamaicon21"})
    headers = {"Authorization": f"Bearer {res_login.json().get('access_token')}"}

    res_avaliacao = requests.post(f"{BASE_URL}/avaliacoes/", json={"nota": 5, "comentario": "Bom", "data_escuta":"2026-10-10", "album_id": 900}, headers=headers)
    assert res_avaliacao.status_code in [400, 404], f"Deveria bloquear fk inexistente. Status {res_avaliacao.status_code}"
