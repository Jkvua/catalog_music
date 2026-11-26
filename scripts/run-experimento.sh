#!/usr/bin/env bash

set -uo pipefail
export LC_ALL=C

# Diretório raiz do projeto
cd "$(dirname "$0")/.."

# Quantidade inicial de repetições
VERSAO="${2:-piloto}"
REPETICOES="${1:-1}"
CENARIO_SELECIONADO="${3:-todos}"
ORDEM_EXECUCAO="${4:-fixa}"

if [[ "$CENARIO_SELECIONADO" != "todos" &&
      "$CENARIO_SELECIONADO" != "a" &&
      "$CENARIO_SELECIONADO" != "b" &&
      "$CENARIO_SELECIONADO" != "c" ]]; then
    echo "Erro: configuração inválida. Use a, b, c ou todos."
    exit 1
fi

if ! [[ "$VERSAO" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "Erro: nome de versão inválido."
    exit 1
fi

if ! [[ "$REPETICOES" =~ ^[1-9][0-9]*$ ]]; then
    echo "Erro: informe um número inteiro positivo de repetições."
    exit 1
fi

if [[ "$ORDEM_EXECUCAO" != "fixa" &&
      "$ORDEM_EXECUCAO" != "balanceada" ]]; then
    echo "Erro: ordem inválida. Use fixa ou balanceada."
    exit 1
fi

if [[ "$ORDEM_EXECUCAO" == "balanceada" &&
      "$CENARIO_SELECIONADO" != "todos" ]]; then
    echo "Erro: a ordem balanceada exige a execução de todos os cenários."
    exit 1
fi

# Diretório dos resultados
IDENTIFICADOR="$(date -u +%Y%m%dt%H%M%Sz)-$$"

RESULTADOS="$PWD/resultados/$VERSAO/$IDENTIFICADOR"
DIRETORIO_RELATIVO="${RESULTADOS#"$PWD/resultados/"}"

mkdir -p "$RESULTADOS"

# Registra os metadados da execução experimental.
GIT_COMMIT="$(git rev-parse HEAD)"
GIT_BRANCH="$(git branch --show-current)"

printf 'identificador,versao,repeticoes_solicitadas,cenario_solicitado,git_commit,git_branch,ordem_execucao\n' \
    > "$RESULTADOS/metadados.csv"

printf '%s,%s,%s,%s,%s,%s,%s\n' \
    "$IDENTIFICADOR" \
    "$VERSAO" \
    "$REPETICOES" \
    "$CENARIO_SELECIONADO" \
    "$GIT_COMMIT" \
    "$GIT_BRANCH" \
    "$ORDEM_EXECUCAO" \
    >> "$RESULTADOS/metadados.csv"

# Arquivo de resumo
echo "versao,repeticao,cenario,categoria,tempo_segundos,codigo_saida" \
    > "$RESULTADOS/resumo.csv"

echo "versao,repeticao,cenario,tempo_total_segundos,codigo_limpeza" \
    > "$RESULTADOS/resumo_cenarios.csv"

echo "versao,repeticao,cenario,posicao" \
    > "$RESULTADOS/ordem_execucao.csv"


# Executa uma categoria de testes e registra seu resultado
executar_testes() {
    local categoria="$1"
    local diretorio="$2"

    local inicio fim tempo
    local codigo_preparacao=0
    local codigo_saida=0

    local arquivo_operacional="$RESULTADOS/repeticao_${REPETICAO}/cenario_${CENARIO}/${categoria}_operacional.csv"

    echo "Executando testes: $categoria"

    printf 'etapa,codigo_saida\n' > "$arquivo_operacional"

    inicio=$(date +%s%N)

    # Prepara o banco de testes e aguarda sua disponibilidade.
    docker compose --profile test up -d --wait db-test \
        || codigo_preparacao=$?

    printf 'preparacao,%s\n' "$codigo_preparacao" \
        >> "$arquivo_operacional"

    if [[ "$codigo_preparacao" -eq 0 ]]; then

        # Executa o pytest sem iniciar novamente as dependências.
        docker compose --profile test run --rm --no-deps \
            tests python -m pytest "tests/$categoria" \
            -v --tb=short \
            --junitxml="/app/resultados/$diretorio/$categoria.xml" \
            || codigo_saida=$?

        printf 'pytest,%s\n' "$codigo_saida" \
            >> "$arquivo_operacional"

    else
        echo "Erro: não foi possível preparar o ambiente para $categoria."
        codigo_saida="$codigo_preparacao"
    fi

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

    local inicio_cenario fim_cenario tempo_total
    local codigo_limpeza=0

    inicio_cenario=$(date +%s%N)

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
        E2E_STATUS_FILE="$PWD/resultados/$diretorio/e2e_operacional.csv" \
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
    docker compose --profile test down -v --remove-orphans \
        || codigo_limpeza=$?

    fim_cenario=$(date +%s%N)
    
    tempo_total=$(awk -v inicio="$inicio_cenario" -v fim="$fim_cenario" \
    'BEGIN {printf "%.3f", (fim-inicio)/1000000000}')

    echo "$VERSAO,$REPETICAO,$CENARIO,$tempo_total,$codigo_limpeza" \
        >> "$RESULTADOS/resumo_cenarios.csv"

    echo "Cenário $CENARIO finalizado."
    echo "Tempo total da configuração: ${tempo_total}s"
    echo "Código de saída da limpeza: $codigo_limpeza"
}

# Define a ordem de execução das configurações em cada repetição
for ((REPETICAO=1; REPETICAO<=REPETICOES; REPETICAO++)); do
    if [[ "$CENARIO_SELECIONADO" == "todos" ]]; then

        if [[ "$ORDEM_EXECUCAO" == "balanceada" ]]; then

            case $(((REPETICAO - 1) % 6)) in
                0) CENARIOS=(a b c) ;;
                1) CENARIOS=(b c a) ;;
                2) CENARIOS=(c a b) ;;
                3) CENARIOS=(a c b) ;;
                4) CENARIOS=(b a c) ;;
                5) CENARIOS=(c b a) ;;
            esac

        else
            CENARIOS=(a b c)
        fi

    else
        CENARIOS=("$CENARIO_SELECIONADO")
    fi

    POSICAO=1

    for CENARIO_ATUAL in "${CENARIOS[@]}"; do

        printf '%s,%s,%s,%s\n' \
            "$VERSAO" \
            "$REPETICAO" \
            "$CENARIO_ATUAL" \
            "$POSICAO" \
            >> "$RESULTADOS/ordem_execucao.csv"

        executar_cenario "$CENARIO_ATUAL"

        POSICAO=$((POSICAO + 1))

    done
done

echo ""
echo "========================================"
echo "Experimento finalizado"
echo "========================================"

cat "$RESULTADOS/resumo.csv"