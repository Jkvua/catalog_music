import csv
import io
import statistics
import zipfile
from pathlib import Path


# Localização dos dados originais
DIRETORIO_ATUAL = Path(__file__).resolve().parent

ARQUIVO_ZIP = (
    DIRETORIO_ATUAL
    / "dados"
    / "resultados-baseline-44572022429.zip"
)


# 1. Ler os arquivos CSV diretamente do ZIP
with zipfile.ZipFile(ARQUIVO_ZIP, "r") as zip_ref:

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
            registro["versao"] == "baseline"
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

# Identificar as execuções classificadas como válidas
execucoes_validas = set()

for registro in registros_validade:
    if registro["status"] == "valida":
        chave = (
            registro["versao"],
            int(registro["repeticao"]),
            registro["cenario"],
        )

        execucoes_validas.add(chave)

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
            registro["versao"] == "baseline"
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

    assert all(codigo == 0 for _, _, codigo in tempos), (
        "Existe uma execução com código de saída diferente de zero."
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

# 3. Percorrer as configurações
print("Versão: baseline")

for cenario in CENARIOS:
    analisar_cenario(cenario, "unitarios")

    if cenario in ["b", "c"]:
        analisar_cenario(cenario, "integracao")

    if cenario == "c":
        analisar_cenario(cenario, "e2e")


print("\n--- TEMPOS TOTAIS DAS CONFIGURAÇÕES ---")
for cenario in CENARIOS:
    analisar_tempo_total(cenario)

