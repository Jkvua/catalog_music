import os
import pytest
import requests
import time

BASE_URL = os.getenv("API_URL", "http://localhost:5000")

def test_isolamento_entre_usuarios():
    """Simula usuário b tentando deletar dados do usuário a"""
    sufixo = str(int(time.time()))

    email_a = f"fatimabernardes{sufixo}@gmail.com"
    requests.post(f"{BASE_URL}/auth/register", json={"user": "Fatima", "email": email_a, "password": "fatimab1090"})
    token_a = requests.post(f"{BASE_URL}/auth/login", json={"email": email_a, "password": "fatimab1090"}).json().get("access_token")
    headers_a = {"Authorization": f"Bearer {token_a}"}

    res_artista_a = requests.post(f"{BASE_URL}/artistas/", json={"nome": f"Tim Bernardes {sufixo}", "genero": "MPB", "pais": "Brasil"}, headers=headers_a)
    assert res_artista_a.status_code == 201, (f"Falha ao criar artista:", f"status={res_artista_a.status_code}," f"resposta={res_artista_a.text}")
    artista_id = res_artista_a.json()["artista"]["id"]

    email_b = f"willianbonner{sufixo}@gmail.com"
    requests.post(f"{BASE_URL}/auth/register", json={"user": "Bonner", "email": email_b, "password": "willbonner"})
    token_b = requests.post(f"{BASE_URL}/auth/login", json={"email": email_b, "password": "willbonner"}).json().get("access_token")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    res_delete_b = requests.delete(f"{BASE_URL}/artistas/{artista_id}", headers=headers_b)
    assert res_delete_b.status_code in [403, 404], f"Deveria bloquear ação de outo usuário. Status: {res_delete_b.status_code}"