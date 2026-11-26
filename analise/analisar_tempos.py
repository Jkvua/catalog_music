import csv
import io
import statistics
import zipfile
from datetime import datetime
from pathlib import Path


# Localização dos dados originais
DIRETORIO_ATUAL = Path(__file__).resolve().parent

ARQUIVOS = {
    "baseline": "resultados-baseline-44572022429.zip",
    "d1": "resultados-d1-44577470488.zip",
    "d2": "resultados-d2-44582644797.zip",
    "d3": "resultados-d3-44591994504.zip",
    "d4": "resultados-d4-44606770151.zip",
    "d5": "resultados-d5-44617969552.zip",
}

def carregar_dados(versao):
    arquivo_zip = DIRETORIO_ATUAL / "dados" / ARQUIVOS[versao]

    with zipfile.ZipFile(arquivo_zip, "r") as zip_ref:

        # Dados dos tempos operacionais
        caminho_resumo = next(
            nome
            for nome in zip_ref.namelist()
            if nome.endswith("/resumo.csv")
        )

        with zip_ref.open(caminho_resumo) as arquivo:
            conteudo = io.TextIOWrapper(arquivo, encoding="utf-8")
            registros = list(csv.DictReader(conteudo))

        # Dados de validade das execuções
        with zip_ref.open("validade_execucoes.csv") as arquivo:
            conteudo = io.TextIOWrapper(arquivo, encoding="utf-8")
            registros_validade = list(csv.DictReader(conteudo))

        # Dados dos tempos totais das configurações
        caminho_resumo_cenarios = next(
            nome
            for nome in zip_ref.namelist()
            if nome.endswith("/resumo_cenarios.csv")
        )

        with zip_ref.open(caminho_resumo_cenarios) as arquivo:
            conteudo = io.TextIOWrapper(arquivo, encoding="utf-8")
            registros_cenarios = list(csv.DictReader(conteudo))

    return registros, registros_validade, registros_cenarios

# Analisar o tempo total de uma configuração
def analisar_tempo_total(cenario):
    tempos = []

    for registro in registros_cenarios:
        chave = (
            registro["versao"],
            int(registro["repeticao"]),
            registro["cenario"],
        )

        if (
            registro["versao"] == VERSAO
            and registro["cenario"] == cenario
            and chave in execucoes_validas
        ):
            tempos.append(
                (
                    int(registro["repeticao"]),
                    float(registro["tempo_total_segundos"]),
                    int(registro["codigo_limpeza"]),
                )
            )

    # Validar os registros
    assert len(tempos) == 5, "Quantidade inesperada de registros."

    assert sorted(rep for rep, _, _ in tempos) == [1, 2, 3, 4, 5], (
        "Repetições ausentes ou duplicadas."
    )

    assert all(codigo == 0 for _, _, codigo in tempos), (
        "Existe uma execução com erro na limpeza."
    )

    # Calcular as estatísticas
    valores = [tempo for _, tempo, _ in tempos]

    media = statistics.mean(valores)
    desvio_padrao = statistics.stdev(valores)
    minimo = min(valores)
    maximo = max(valores)

    # Apresentar os resultados
    print(f"\nConfiguração: {cenario.upper()}")
    print("Métrica: Tempo total da configuração")

    print("\nTempos registrados:")

    for repeticao, tempo, _ in sorted(tempos):
        print(f"Repetição {repeticao}: {tempo:.3f} s")

    print("\nEstatísticas:")
    print(f"Média: {media:.3f} s")
    print(f"Desvio-padrão amostral: {desvio_padrao:.3f} s")
    print(f"Mínimo: {minimo:.3f} s")
    print(f"Máximo: {maximo:.3f} s")
    return {
        "media": media,
        "desvio_padrao": desvio_padrao,
        "minimo": minimo,
        "maximo": maximo
    }

# Configurações que serão analisadas
CENARIOS = ["a", "b", "c"]

# 2. Analisar os tempos de uma configuração
def analisar_cenario(cenario, categoria):
    tempos = []

    for registro in registros:
        chave = (
            registro["versao"],
            int(registro["repeticao"]),
            registro["cenario"],
        )

        if (
            registro["versao"] == VERSAO
            and registro["cenario"] == cenario
            and registro["categoria"] == categoria
            and chave in execucoes_validas
        ):
            tempos.append(
                (
                    int(registro["repeticao"]),
                    float(registro["tempo_segundos"]),
                    int(registro["codigo_saida"]),
                )
            )

    # Validar os registros
    assert len(tempos) == 5, "Quantidade inesperada de registros."

    assert sorted(rep for rep, _, _ in tempos) == [1, 2, 3, 4, 5], (
        "Repetições ausentes ou duplicadas."
    )

    assert all(codigo in (0, 1) for _, _, codigo in tempos), (
        "Existe uma execução com código de saída inesperado."
    )

    # Calcular as estatísticas
    valores = [tempo for _, tempo, _ in tempos]

    media = statistics.mean(valores)
    desvio_padrao = statistics.stdev(valores)
    minimo = min(valores)
    maximo = max(valores)

    # Apresentar os resultados
    print(f"\nConfiguração: {cenario.upper()}")
    print(f"Categoria: {categoria.capitalize()}")

    print("\nTempos registrados:")

    for repeticao, tempo, _ in sorted(tempos):
        print(f"Repetição {repeticao}: {tempo:.3f} s")

    print("\nEstatísticas:")
    print(f"Média: {media:.3f} s")
    print(f"Desvio-padrão amostral: {desvio_padrao:.3f} s")
    print(f"Mínimo: {minimo:.3f} s")
    print(f"Máximo: {maximo:.3f} s")
    return {
        "media": media,
        "desvio_padrao": desvio_padrao,
        "minimo": minimo,
        "maximo": maximo,
    }

def analisar_tempo_conjunto(cenario):
    tempos_por_repeticao = {}

    categorias_esperadas = {
        "a": {"unitarios"},
        "b": {"unitarios", "integracao"},
        "c": {"unitarios", "integracao", "e2e"},
    }

    categorias_por_repeticao = {}

    for registro in registros:
        chave = (
            registro["versao"],
            int(registro["repeticao"]),
            registro["cenario"],
        )

        if (
            registro["versao"] == VERSAO
            and registro["cenario"] == cenario
            and chave in execucoes_validas
        ):
            repeticao = int(registro["repeticao"])
            tempo = float(registro["tempo_segundos"])
            categoria = registro["categoria"]

            assert categoria in categorias_esperadas[cenario], (
                f"Categoria inesperada: {categoria}"
            )

            if repeticao not in categorias_por_repeticao:
                categorias_por_repeticao[repeticao] = set()

            assert categoria not in categorias_por_repeticao[repeticao], (
                f"Categoria duplicada na repetição {repeticao}: {categoria}"
            )

            categorias_por_repeticao[repeticao].add(categoria)

            if repeticao not in tempos_por_repeticao:
                tempos_por_repeticao[repeticao] = 0.0

            tempos_por_repeticao[repeticao] += tempo

    assert sorted(tempos_por_repeticao) == [1, 2, 3, 4, 5], (
        "Repetições ausentes ou inesperadas."
    )

    for repeticao, categorias in categorias_por_repeticao.items():
        assert categorias == categorias_esperadas[cenario], (
            f"Categorias incompletas na repetição {repeticao}: {categorias}"
        )

    # Calcular as estatísticas dos tempos conjuntos
    valores = [
        tempos_por_repeticao[repeticao]
        for repeticao in sorted(tempos_por_repeticao)
    ]

    media = statistics.mean(valores)
    desvio_padrao = statistics.stdev(valores)
    minimo = min(valores)
    maximo = max(valores)

    return {
        "media": media,
        "desvio_padrao": desvio_padrao,
        "minimo": minimo,
        "maximo": maximo,
    }

def analisar_tempo_pipeline():
    caminho_csv = DIRETORIO_ATUAL / "dados" / "tempos_workflows.csv"

    with open(caminho_csv, newline="", encoding="utf-8") as arquivo:
        registros_pipeline = list(csv.DictReader(arquivo))

    # Validar a quantidade de registros
    assert len(registros_pipeline) == len(ARQUIVOS), (
        "Quantidade inesperada de registros de workflows."
    )

    resultados = {}

    for registro in registros_pipeline:
        versao = registro["versao"]
        run_id = registro["run_id"]

        assert versao in ARQUIVOS, (
            f"Versão inesperada: {versao}"
        )

        assert versao not in resultados, (
            f"Versão duplicada: {versao}"
        )

        assert run_id == ARQUIVOS[versao].removesuffix(".zip").rsplit("-", 1)[-1], (
            f"Run ID incompatível com a versão {versao}"
        )

        inicio = datetime.fromisoformat(
            registro["run_started_at"].replace("Z", "+00:00")
        )

        ultima_atualizacao = datetime.fromisoformat(
            registro["updated_at"].replace("Z", "+00:00")
        )

        duracao = (ultima_atualizacao - inicio).total_seconds()

        assert duracao >= 0, (
            f"Duração negativa para a versão {versao}"
        )

        resultados[versao] = duracao

    assert set(resultados) == set(ARQUIVOS), (
        "Existem versões ausentes nos registros de workflows."
    )

    return resultados

def analisar_tempos_agregados(resultados_experimento):
    versoes_experimentais = ["d1", "d2", "d3", "d4", "d5"]

    assert all(
        versao in resultados_experimento
        for versao in versoes_experimentais
    ), "Existem versões experimentais ausentes."

    resultados_agregados = {}

    for cenario in CENARIOS:
        medias = [
            resultados_experimento[versao]["totais"][cenario]["media"]
            for versao in versoes_experimentais
        ]

        resultados_agregados[cenario] = statistics.mean(medias)

    return resultados_agregados

# 3. Percorrer as configurações
def executar_analises():
    print(f"Versão: {VERSAO}")

    resultados_niveis = {}

    for cenario in CENARIOS:
        resultados_niveis[cenario] = {}

        resultados_niveis[cenario]["unitarios"] = analisar_cenario(cenario, "unitarios")

        if cenario in ["b", "c"]:
            resultados_niveis[cenario]["integracao"] = analisar_cenario(cenario, "integracao")

        if cenario == "c":
            resultados_niveis[cenario]["e2e"] = analisar_cenario(cenario, "e2e")

    print("\n--- TEMPOS TOTAIS DAS CONFIGURAÇÕES ---")

    resultados_totais = {}

    for cenario in CENARIOS:
        resultados_totais[cenario] = analisar_tempo_total(cenario)

    resultados_conjuntos = {}

    for cenario in CENARIOS:
        resultados_conjuntos[cenario] = analisar_tempo_conjunto(cenario)

    return {
        "niveis": resultados_niveis,
        "conjuntos": resultados_conjuntos,
        "totais": resultados_totais,
    }

resultados_experimento = {}

for versao in ARQUIVOS:
    VERSAO = versao
    registros, registros_validade, registros_cenarios = carregar_dados(VERSAO)

    execucoes_validas = set()

    for registro in registros_validade:
        if registro["status"] == "valida":
            chave = (
                registro["versao"],
                int(registro["repeticao"]),
                registro["cenario"],
            )
            execucoes_validas.add(chave)

    print("\n" + "=" * 50)
    resultados_experimento[VERSAO] = executar_analises()

print("\n--- TABELA CONSOLIDADA: TEMPOS TOTAIS (s) ---")
print("Valores apresentados como média ± desvio-padrão amostral")
print(f"{'Versão':<12} {'A':>18} {'B':>18} {'C':>18}")

for versao, resultados in resultados_experimento.items():
    resultados = resultados["totais"]
    valores = []

    for cenario in CENARIOS:
        media = resultados[cenario]["media"]
        desvio = resultados[cenario]["desvio_padrao"]

        valores.append(f"{media:.3f} ± {desvio:.3f}")

    print(f"{versao:<12} {valores[0]:>18} {valores[1]:>18} {valores[2]:>18}")

print("\n--- TABELA CONSOLIDADA: MÍNIMO E MÁXIMO (s) ---")
print(f"{'Versão':<12} {'A':>18} {'B':>18} {'C':>18}")

for versao, resultados in resultados_experimento.items():
    resultados = resultados["totais"]
    valores = []

    for cenario in CENARIOS:
        minimo = resultados[cenario]["minimo"]
        maximo = resultados[cenario]["maximo"]

        valores.append(f"{minimo:.3f} – {maximo:.3f}")

    print(f"{versao:<12} {valores[0]:>18} {valores[1]:>18} {valores[2]:>18}")

print("\n--- TABELA CONSOLIDADA: TEMPO POR NÍVEL DE TESTE (s) ---")
print("Valores apresentados como média ± desvio-padrão amostral")

print(f"{'Versão':<12} {'Config.':<10} {'Nível':<15} {'Tempo (s)':>20}")

for versao, resultados in resultados_experimento.items():
    for cenario, categorias in resultados["niveis"].items():
        for categoria, estatisticas in categorias.items():
            media = estatisticas["media"]
            desvio = estatisticas["desvio_padrao"]

            tempo = f"{media:.3f} ± {desvio:.3f}"

            print(
                f"{versao:<12} "
                f"{cenario.upper():<10} "
                f"{categoria:<15} "
                f"{tempo:>20}"
            )

print("\n--- TABELA CONSOLIDADA: MÍNIMO E MÁXIMO POR NÍVEL (s) ---")

print(f"{'Versão':<12} {'Config.':<10} {'Nível':<15} {'Intervalo (s)':>20}")

for versao, resultados in resultados_experimento.items():
    for cenario, categorias in resultados["niveis"].items():
        for categoria, estatisticas in categorias.items():
            minimo = estatisticas["minimo"]
            maximo = estatisticas["maximo"]

            intervalo = f"{minimo:.3f} – {maximo:.3f}"

            print(
                f"{versao:<12} "
                f"{cenario.upper():<10} "
                f"{categoria:<15} "
                f"{intervalo:>20}"
            )

print("\n--- TABELA CONSOLIDADA: TEMPO CONJUNTO DOS TESTES (s) ---")
print("Valores apresentados como média ± desvio-padrão amostral")
print(f"{'Versão':<12} {'A':>18} {'B':>18} {'C':>18}")

for versao, resultados in resultados_experimento.items():
    conjuntos = resultados["conjuntos"]
    valores = []

    for cenario in CENARIOS:
        media = conjuntos[cenario]["media"]
        desvio = conjuntos[cenario]["desvio_padrao"]

        valores.append(f"{media:.3f} ± {desvio:.3f}")

    print(
        f"{versao:<12} "
        f"{valores[0]:>18} "
        f"{valores[1]:>18} "
        f"{valores[2]:>18}"
    )

print("\n--- TABELA CONSOLIDADA: MÍNIMOS E MÁXIMOS DO TEMPO CONJUNTO (s) ---")
print(f"{'Versão':<12} {'A':>18} {'B':>18} {'C':>18}")

for versao, resultados in resultados_experimento.items():
    conjuntos = resultados["conjuntos"]
    valores = []

    for cenario in CENARIOS:
        minimo = conjuntos[cenario]["minimo"]
        maximo = conjuntos[cenario]["maximo"]

        valores.append(f"{minimo:.3f} – {maximo:.3f}")

    print(
        f"{versao:<12} "
        f"{valores[0]:>18} "
        f"{valores[1]:>18} "
        f"{valores[2]:>18}"
    )

print("\n--- TABELA CONSOLIDADA: TEMPO TOTAL DO PIPELINE (s) ---")

resultados_pipeline = analisar_tempo_pipeline()

print(f"{'Versão':<12} {'Tempo (s)':>15}")

for versao in ARQUIVOS:
    tempo = resultados_pipeline[versao]

    print(f"{versao:<12} {tempo:>15.3f}")

print("\n--- TEMPO TOTAL MÉDIO POR CONFIGURAÇÃO (D1-D5) ---")

resultados_agregados = analisar_tempos_agregados(
    resultados_experimento
)

print(f"{'Configuração':<15} {'Tempo médio (s)':>20}")

for cenario in CENARIOS:
    media = resultados_agregados[cenario]

    print(f"{cenario.upper():<15} {media:>20.3f}")


print("\n--- COMPARAÇÃO INCREMENTAL DOS TEMPOS ---")

transicoes = [
    ("a", "b"),
    ("b", "c"),
]

for origem, destino in transicoes:
    tempo_origem = resultados_agregados[origem]
    tempo_destino = resultados_agregados[destino]

    diferenca = tempo_destino - tempo_origem
    aumento_percentual = (diferenca / tempo_origem) * 100

    print(f"\n{origem.upper()} -> {destino.upper()}")
    print(f"Aumento absoluto: {diferenca:.3f} s")
    print(f"Aumento percentual: {aumento_percentual:.2f}%")