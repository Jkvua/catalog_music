from app.schemas.avaliacao import avaliacao_schema, avaliacoes_schema

def test_validar_avaliacao_schema():
    """Testa se o schema da avaliacao completa e correta passa corretamente"""
    dados = {"nota": 5, 
             "comentario": "Álbum lindo, extremamente emocionante", 
             "data_escuta": "2026-10-08",
             "album_id": 1,
             "usuario_id": 1
            }

    erros = avaliacao_schema.validate(dados)
    assert not erros

def test_avaliacao_schema_campos_obrigatorios():
    """Testa se o schema barra sem os campos obrigatorios"""
    dados_vazio = {"cometario": "Bem mais ou menos, feito na pressa"    }
    erros = avaliacao_schema.validate(dados_vazio)
    assert "nota" in erros

def test_avaliacao_limite_nota():
    """Testa se aceita nota apenas entre os valores 1 e 5"""
    dados_nota_zero = {"nota":0}
    erros_zero = avaliacao_schema.validate(dados_nota_zero)
    assert "nota" in erros_zero

    dados_nota_seis = {"nota":6}
    erros_seis = avaliacao_schema.validate(dados_nota_seis)
    assert "nota" in erros_seis

def test_avaliacao_limite_comentario():
    """Testa se comentario com mais de 500 caracteres é barrado"""
    dados_comentario_gigante = {"nota": 5, "comentario": "A" * 501}
    erros_gigante = avaliacao_schema.validate(dados_comentario_gigante)
    assert "comentario" in erros_gigante

def test_avaliacao_data_invalida():
    """Testa se data de escuta invalida, barras formatos que não sejam YYYY-MM-DD"""
    dados_data_invalida = {"nota": 3, "data_escuta": "08/10/2026"}
    erros_data_invalida = avaliacao_schema.validate(dados_data_invalida)
    assert "data_escuta" in erros_data_invalida