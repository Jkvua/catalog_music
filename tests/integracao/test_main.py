def test_index_routes_sucesso(client):
    """Garante resposta 200 para rotas e lista endpoints"""
    response = client.get('/')

    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Bem-vindo ao Catalog Music API!"
    assert "rotas disponiveis" in data
    assert isinstance(data["rotas disponiveis"], list)
