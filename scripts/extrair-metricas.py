import csv
import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
RESULTADOS = RAIZ_PROJETO / "resultados"

CATEGORIAS = {
    "a": ["unitarios"],
    "b": ["unitarios", "integracao"],
    "c": ["unitarios", "integracao", "e2e"],
}

CAMPOS_METRICAS = [
    "versao",
    "execucao",
    "repeticao",
    "cenario",
    "categoria",
    "total",
    "aprovados",
    "falhas",
    "erros",
    "ignorados",
    "tempo_pytest_segundos",
]

CAMPOS_VALIDADE = [
    "versao",
    "execucao",
    "repeticao",
    "cenario",
    "status",
    "motivo",
]


def ler_csv(caminho):
    with caminho.open(newline="", encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo))


def analisar_xml(caminho):
    try:
        raiz = ET.parse(caminho).getroot()

        if raiz.tag == "testsuite":
            suites = [raiz]
        elif raiz.tag == "testsuites":
            suites = raiz.findall("testsuite")
        else:
            raise ValueError("Estrutura XML desconhecida")

        if len(suites) != 1:
            raise ValueError("Quantidade inesperada de suites")

        suite = suites[0]

        total = int(suite.attrib["tests"])
        falhas = int(suite.attrib["failures"])
        erros = int(suite.attrib["errors"])
        ignorados = int(suite.attrib["skipped"])
        tempo = float(suite.attrib["time"])

        casos = suite.findall(".//testcase")

        if total <= 0:
            raise ValueError("Nenhum teste registrado")

        if len(casos) != total:
            raise ValueError("Quantidade de casos inconsistente")

        falhas_encontradas = sum(
            caso.find("failure") is not None
            for caso in casos
        )

        erros_encontrados = sum(
            caso.find("error") is not None
            for caso in casos
        )

        ignorados_encontrados = sum(
            caso.find("skipped") is not None
            for caso in casos
        )

        if (
            falhas != falhas_encontradas
            or erros != erros_encontrados
            or ignorados != ignorados_encontrados
        ):
            raise ValueError("Contagens de resultados inconsistentes")

        if min(falhas, erros, ignorados, tempo) < 0:
            raise ValueError("Metrica negativa")

        if falhas + erros + ignorados > total:
            raise ValueError("Contagens inconsistentes")

        return {
            "total": total,
            "aprovados": total - falhas - erros - ignorados,
            "falhas": falhas,
            "erros": erros,
            "ignorados": ignorados,
            "tempo_pytest_segundos": tempo,
        }

    except (ET.ParseError, ValueError, KeyError) as erro:
        raise ValueError(f"Relatorio invalido: {erro}") from erro

def validar_completude(caminho, categoria, referencia):
    raiz = ET.parse(caminho).getroot()

    encontrados = [
        (caso.get("classname"), caso.get("name"))
        for caso in raiz.findall(".//testcase")
    ]

    esperados = [
        tuple(identificador)
        for identificador in referencia[categoria]
    ]

    if len(encontrados) != len(set(encontrados)):
        raise ValueError("Identificadores de testes duplicados")

    if set(encontrados) != set(esperados):
        raise ValueError("Testes ausentes ou inesperados")


def validar_e2e(diretorio, codigo_teste):
    caminho = diretorio / "e2e_operacional.csv"

    if not caminho.is_file():
        return "revisar", "registro_operacional_e2e_ausente"

    try:
        registros = ler_csv(caminho)
        etapas = {}

        for registro in registros:
            etapa = registro["etapa"]

            if etapa in etapas:
                return "invalida", "etapa_e2e_duplicada"

            etapas[etapa] = registro["codigo_saida"]

        if set(etapas) != {"preparacao", "pytest", "limpeza"}:
            return "invalida", "registro_e2e_incompleto"

        if etapas["preparacao"] != "0":
            return "invalida", "falha_preparacao_e2e"

        if etapas["limpeza"] != "0":
            return "invalida", "falha_limpeza_e2e"

        if etapas["pytest"] != codigo_teste:
            return "invalida", "codigos_e2e_inconsistentes"

    except (OSError, KeyError, csv.Error):
        return "invalida", "registro_e2e_ilegivel"

    return "valida", "registro_e2e_completo"

def validar_operacional(diretorio, categoria, codigo_teste):
    caminho = diretorio / f"{categoria}_operacional.csv"

    if not caminho.is_file():
        return "invalida", f"registro_operacional_ausente_{categoria}"

    try:
        registros = ler_csv(caminho)
        etapas = {}

        for registro in registros:
            etapa = registro["etapa"]

            if etapa in etapas:
                return "invalida", f"etapa_duplicada_{categoria}"

            etapas[etapa] = registro["codigo_saida"]

        if set(etapas) not in (
            {"preparacao", "pytest"},
            {"preparacao"},
        ):
            return "invalida", f"registro_operacional_incompleto_{categoria}"

        if etapas["preparacao"] != "0":
            return "invalida", f"falha_preparacao_{categoria}"

        if "pytest" not in etapas:
            return "invalida", f"pytest_nao_executado_{categoria}"

        if etapas["pytest"] != codigo_teste:
            return "invalida", f"codigos_inconsistentes_{categoria}"

    except (OSError, KeyError, csv.Error):
        return "invalida", f"registro_operacional_ilegivel_{categoria}"

    return "valida", "registro_operacional_completo"

def validar_cenario(diretorio, cenario, repeticao, registros_testes, metricas, referencia):
    esperadas = CATEGORIAS[cenario]
    motivos_invalidos = []
    motivos_revisao = []
    categorias_com_falhas = []

    encontrados = {}

    for registro in registros_testes:
        categoria = registro["categoria"]

        if categoria in encontrados:
            motivos_invalidos.append("categoria_duplicada")
        else:
            encontrados[categoria] = registro

    if set(encontrados) != set(esperadas):
        motivos_invalidos.append("categorias_incompletas")

    xml_encontrados = {arquivo.stem for arquivo in diretorio.glob("*.xml")}

    if xml_encontrados != set(esperadas):
        motivos_invalidos.append("relatorios_incompletos")

    for categoria in esperadas:
        caminho = diretorio / f"{categoria}.xml"

        if not caminho.is_file():
            continue

        try:
            dados = analisar_xml(caminho)
            validar_completude(caminho, categoria, referencia)
            metricas.append({
                "versao": diretorio.parents[2].name,
                "execucao": diretorio.parents[1].name,
                "repeticao": repeticao,
                "cenario": cenario,
                "categoria": categoria,
                **dados,
            })

        except ValueError as erro:
            if "Testes ausentes ou inesperados" in str(erro):
                motivos_invalidos.append(f"testes_incompletos_{categoria}")
            elif "Identificadores de testes duplicados" in str(erro):
                motivos_invalidos.append(f"testes_duplicados_{categoria}")
            else:
                motivos_invalidos.append(f"xml_invalido_{categoria}")
            continue

        registro = encontrados.get(categoria)

        if registro is None:
            continue

        codigo = registro["codigo_saida"]

        if codigo == "0":
            if dados["falhas"] > 0 or dados["erros"] > 0:
                motivos_revisao.append(f"codigo_inconsistente_{categoria}")

        elif codigo == "1":
            if dados["falhas"] > 0 and dados["erros"] == 0:
                categorias_com_falhas.append(categoria)
            elif dados["erros"] > 0:
                motivos_revisao.append(f"verificar_erros_{categoria}")
            else:
                motivos_revisao.append(f"saida_1_sem_falhas_{categoria}")

        else:
            motivos_invalidos.append(f"execucao_interrompida_{categoria}")

        if categoria == "e2e":
            status, motivo = validar_e2e(diretorio, codigo)
        else:
            status, motivo = validar_operacional(
                diretorio,
                categoria,
                codigo,
            )

        if status == "invalida":
            motivos_invalidos.append(motivo)
        elif status == "revisar":
            motivos_revisao.append(motivo)

    if motivos_invalidos:
        return "invalida", ";".join(sorted(set(motivos_invalidos)))

    if motivos_revisao:
        return "revisar", ";".join(sorted(set(motivos_revisao)))

    if categorias_com_falhas:
        return "valida", "execucao_completa_com_falhas"

    return "valida", "execucao_completa"


def salvar_csv(caminho, campos, registros):
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(registros)

def obter_repeticoes_esperadas(diretorio_execucao, registros_testes, registros_cenarios):
    caminho_metadados = diretorio_execucao / "metadados.csv"

    if caminho_metadados.is_file():
        registros = ler_csv(caminho_metadados)

        if len(registros) != 1:
            raise ValueError(
                f"Quantidade invalida de registros em {caminho_metadados}"
            )

        quantidade = int(registros[0]["repeticoes_solicitadas"])

        if quantidade <= 0:
            raise ValueError(
                "A quantidade de repeticoes solicitadas deve ser positiva."
            )

        return [str(numero) for numero in range(1, quantidade + 1)]

    # Compatibilidade com os pilotos anteriores, sem metadados.
    return sorted(
        {
            registro["repeticao"]
            for registro in registros_testes + registros_cenarios
        },
        key=int,
    )

def processar_execucao(diretorio_execucao, metricas, validade, referencia):
    caminho_resumo = diretorio_execucao / "resumo.csv"
    caminho_cenarios = diretorio_execucao / "resumo_cenarios.csv"

    if not caminho_resumo.is_file() or not caminho_cenarios.is_file():
        print(f"Execucao sem resumos completos: {diretorio_execucao}")
        return

    registros_testes = ler_csv(caminho_resumo)
    registros_cenarios = ler_csv(caminho_cenarios)

    repeticoes = obter_repeticoes_esperadas(
        diretorio_execucao,
        registros_testes,
        registros_cenarios,
    )

    cenarios_esperados = obter_cenarios_esperados(diretorio_execucao)

    for repeticao in repeticoes:
        for cenario in cenarios_esperados:

            registros_cenario = [
                registro
                for registro in registros_cenarios
                if registro["repeticao"] == repeticao
                and registro["cenario"] == cenario
            ]

            if not registros_cenario:
                validade.append({
                    "versao": diretorio_execucao.parent.name,
                    "execucao": diretorio_execucao.name,
                    "repeticao": repeticao,
                    "cenario": cenario,
                    "status": "invalida",
                    "motivo": "cenario_nao_executado",
                })
                continue

            if len(registros_cenario) > 1:
                validade.append({
                    "versao": diretorio_execucao.parent.name,
                    "execucao": diretorio_execucao.name,
                    "repeticao": repeticao,
                    "cenario": cenario,
                    "status": "invalida",
                    "motivo": "registro_cenario_duplicado",
                })
                continue

            registro = registros_cenario[0]

            diretorio = (
                diretorio_execucao
                / f"repeticao_{repeticao}"
                / f"cenario_{cenario}"
            )

            testes_cenario = [
                item for item in registros_testes
                if item["repeticao"] == repeticao
                and item["cenario"] == cenario
            ]

            status, motivo = validar_cenario(
                diretorio,
                cenario,
                repeticao,
                testes_cenario,
                metricas,
                referencia,
            )

            if registro["codigo_limpeza"] != "0":
                status = "invalida"
                motivo += ";falha_limpeza_cenario"

            validade.append({
                "versao": diretorio_execucao.parent.name,
                "execucao": diretorio_execucao.name,
                "repeticao": repeticao,
                "cenario": cenario,
                "status": status,
                "motivo": motivo,
            })

def obter_cenarios_esperados(diretorio_execucao):
    caminho_metadados = diretorio_execucao / "metadados.csv"

    if not caminho_metadados.is_file():
        return list(CATEGORIAS)

    registros = ler_csv(caminho_metadados)

    if len(registros) != 1:
        raise ValueError("Quantidade invalida de registros nos metadados")

    cenario = registros[0].get("cenario_solicitado", "todos")

    if cenario == "todos":
        return list(CATEGORIAS)

    if cenario not in CATEGORIAS:
        raise ValueError(f"Cenario solicitado invalido: {cenario}")

    return [cenario]

def main():
    metricas = []
    validade = []

    caminho_referencia = RESULTADOS / "referencia_testes.json"

    with caminho_referencia.open(encoding="utf-8") as arquivo:
        referencia = json.load(arquivo)

    if len(sys.argv) > 1:
        execucoes = [Path(sys.argv[1]).resolve()]
    else:
        execucoes = sorted(
            caminho.parent
            for caminho in RESULTADOS.glob("*/*/resumo_cenarios.csv")
        )

    for diretorio in execucoes:
        processar_execucao(diretorio, metricas, validade, referencia)

    salvar_csv(
        RESULTADOS / "metricas_testes.csv",
        CAMPOS_METRICAS,
        metricas,
    )

    salvar_csv(
        RESULTADOS / "validade_execucoes.csv",
        CAMPOS_VALIDADE,
        validade,
    )

    print(f"Metricas extraidas: {len(metricas)} relatorios.")
    print(f"Configuracoes avaliadas: {len(validade)}")

    for registro in validade:
        print(
            f"{registro['versao']} | "
            f"{registro['repeticao']} | "
            f"{registro['cenario']} | "
            f"{registro['status']} | "
            f"{registro['motivo']}"
        )


if __name__ == "__main__":
    main()