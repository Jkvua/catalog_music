import os
import pytest
import requests
import time

BASE_URL = os.getenv("API_URL", "http://localhost:5000")

def test_acesso_sem_token():
    """Simula requisições em enviar o token"""
    res_me = requests.get(f"{BASE_URL}/usuarios/me")
    assert res_me.status_code == 401, f"Acesso sem token não foi bloqueado: {res_me.text}"

    res_artista = requests.post(f"{BASE_URL}/artistas/", json={"nome": "Young Miko", "genero": "Trap", "paia": "Porto Rico"})
    assert res_artista.status_code == 401, f"Criação sem tokem foi bloqueada: {res_artista.text}"

def test_acesso_token_invalido():
    """Simula requisição com o token incorreto ou inválido"""
    headers = {"Authorization": "Bearer token_completamente_errado"}
    res_me = requests.get(f"{BASE_URL}/usuarios/me", headers=headers)
    assert res_me.status_code in [401, 422], f"Deveria bloquear token inválido. Status: {res_me.status_code}"