#!/usr/bin/env bash

set -uo pipefail
export LC_ALL=C

# Diretório raiz do projeto
cd "$(dirname "$0")/.."

# Quantidade inicial de repetições
VERSAO="${2:-piloto}"
REPETICOES="${1:-1}"

if ! [[ "$VERSAO" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "Erro: nome de versão inválido."
    exit 1
fi

if ! [[ "$REPETICOES" =~ ^[1-9][0-9]*$ ]]; then
    echo "Erro: informe um número inteiro positivo de repetições."
    exit 1
fi

# Diretório dos resultados
IDENTIFICADOR="$(date -u +%Y%m%dt%H%M%Sz)-$$"

RESULTADOS="$PWD/resultados/$VERSAO/$IDENTIFICADOR"
DIRETORIO_RELATIVO="${RESULTADOS#"$PWD/resultados/"}"

mkdir -p "$RESULTADOS"

# Arquivo de resumo
echo "versao,repeticao,cenario,categoria,tempo_segundos,codigo_saida" \
    > "$RESULTADOS/resumo.csv"


# Executa uma categoria de testes e registra seu resultado
executar_testes() {
    local categoria="$1"
    local diretorio="$2"

    local inicio fim tempo
    local codigo_saida=0

    echo "Executando testes: $categoria"

    inicio=$(date +%s%N)

    docker compose --profile test run --rm \
        tests python -m pytest "tests/$categoria" \
        -v --tb=short \
        --junitxml="/app/resultados/$diretorio/$categoria.xml" \
        || codigo_saida=$?

    fim=$(date +%s%N)

    tempo=$(awk -v inicio="$inicio" -v fim="$fim" \
        'BEGIN {printf "%.3f", (fim-inicio)/1000000000}')

    echo "$VERSAO,$REPETICAO,$CENARIO,$categoria,$tempo,$codigo_saida" \
        >> "$RESULTADOS/resumo.csv"

    echo "Categoria $categoria finalizada."
    echo "Tempo: ${tempo}s"
    echo "Código de saída: $codigo_saida"
}


# Executa um cenário experimental
executar_cenario() {
    CENARIO="$1"

    local diretorio="$DIRETORIO_RELATIVO/repeticao_${REPETICAO}/cenario_${CENARIO}"

    # Projeto Docker isolado para cada cenário e repetição
    export COMPOSE_PROJECT_NAME="exp-${GITHUB_RUN_ID:-local}-${GITHUB_RUN_ATTEMPT:-1}-${IDENTIFICADOR}-${REPETICAO}-${CENARIO}"

    mkdir -p "$PWD/resultados/$diretorio"

    echo ""
    echo "========================================"
    echo "Repetição $REPETICAO - Cenário $CENARIO"
    echo "========================================"

    # Todos os cenários executam testes unitários
    executar_testes unitarios "$diretorio"

    # Cenários B e C também executam integração
    if [[ "$CENARIO" == "b" || "$CENARIO" == "c" ]]; then
        executar_testes integracao "$diretorio"
    fi

    # Cenário C também executa E2E
    if [[ "$CENARIO" == "c" ]]; then

        local inicio fim tempo
        local codigo_saida=0

        inicio=$(date +%s%N)

        JUNIT_XML="/app/resultados/$diretorio/e2e.xml" \
            bash scripts/run-e2e.sh \
            || codigo_saida=$?

        fim=$(date +%s%N)

        tempo=$(awk -v inicio="$inicio" -v fim="$fim" \
            'BEGIN {printf "%.3f", (fim-inicio)/1000000000}')

        echo "$VERSAO,$REPETICAO,$CENARIO,e2e,$tempo,$codigo_saida" \
            >> "$RESULTADOS/resumo.csv"

        echo "E2E finalizado."
        echo "Tempo: ${tempo}s"
        echo "Código de saída: $codigo_saida"
    fi

    # Limpa os recursos do projeto experimental atual
    docker compose --profile test down -v --remove-orphans

    echo "Cenário $CENARIO finalizado."
}


# Execução do experimento
for ((REPETICAO=1; REPETICAO<=REPETICOES; REPETICAO++)); do

    executar_cenario a
    executar_cenario b
    executar_cenario c

done

echo ""
echo "========================================"
echo "Experimento finalizado"
echo "========================================"

cat "$RESULTADOS/resumo.csv"