#!/bin/bash
# Script de desenvolvimento para FastMCP MongoDB Server

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERRO]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Função para verificar se o comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Função para verificar dependências
check_dependencies() {
    local deps=("python3" "pip")
    local missing=()
    
    for dep in "${deps[@]}"; do
        if ! command_exists "$dep"; then
            missing+=("$dep")
        fi
    done
    
    if [ ${#missing[@]} -ne 0 ]; then
        error "Dependências faltando: ${missing[*]}"
        exit 1
    fi
}

# Função para ativar ambiente virtual
activate_venv() {
    if [ ! -d "venv" ]; then
        log "Criando ambiente virtual..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    log "Ambiente virtual ativado"
}

# Função para instalar dependências
install_deps() {
    log "Instalando dependências..."
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    log "Dependências instaladas"
}

# Função para iniciar ambiente de desenvolvimento
up() {
    log "Iniciando ambiente de desenvolvimento..."
    
    activate_venv
    install_deps
    
    log "Ambiente de desenvolvimento iniciado!"
    log "Para executar o servidor: python -m src.main"
    log "Para executar testes: ./scripts/dev.sh test"
}

# Função para executar testes
test() {
    log "Executando testes..."
    activate_venv
    
    # Executa testes com cobertura
    python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html
    
    log "Testes concluídos. Relatório de cobertura em htmlcov/"
}

# Função para verificar qualidade do código
lint() {
    log "Verificando qualidade do código..."
    activate_venv
    
    # Black - formatação
    log "Executando Black..."
    black --check src/ tests/
    
    # isort - import sorting
    log "Executando isort..."
    isort --check-only src/ tests/
    
    # flake8 - linting
    log "Executando flake8..."
    flake8 src/ tests/
    
    # mypy - type checking
    log "Executando mypy..."
    mypy src/
    
    log "Verificação de qualidade concluída"
}

# Função para formatar código
format() {
    log "Formatando código..."
    activate_venv
    
    black src/ tests/
    isort src/ tests/
    
    log "Código formatado"
}

# Função para executar o servidor
run() {
    log "Executando servidor FastMCP MongoDB..."
    activate_venv
    
    # Verifica se MongoDB está rodando
    if ! command_exists "mongosh" && ! command_exists "mongo"; then
        warning "MongoDB não detectado. Certifique-se de que está rodando na porta 27017"
    fi
    
    python -m src.main
}

# Função para executar servidor em modo debug
debug() {
    log "Executando servidor em modo debug..."
    activate_venv
    
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    export LOG_LEVEL=DEBUG
    export DEBUG=true
    
    python -m src.main
}

# Função para limpar ambiente
clean() {
    log "Limpando ambiente..."
    
    # Remove arquivos temporários
    rm -rf __pycache__/
    rm -rf .pytest_cache/
    rm -rf htmlcov/
    rm -rf .coverage
    rm -rf .mypy_cache/
    rm -rf .dmypy.json
    
    # Remove ambiente virtual
    if [ -d "venv" ]; then
        rm -rf venv
        log "Ambiente virtual removido"
    fi
    
    log "Ambiente limpo"
}

# Função para mostrar ajuda
help() {
    echo "Script de desenvolvimento para FastMCP MongoDB Server"
    echo ""
    echo "Uso: $0 [COMANDO]"
    echo ""
    echo "Comandos:"
    echo "  up          Configura ambiente de desenvolvimento"
    echo "  test        Executa testes"
    echo "  lint        Verifica qualidade do código"
    echo "  format      Formata código automaticamente"
    echo "  run         Executa o servidor"
    echo "  debug       Executa servidor em modo debug"
    echo "  clean       Limpa ambiente completamente"
    echo "  help        Mostra esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0 up       # Configura ambiente"
    echo "  $0 test     # Executa testes"
    echo "  $0 lint     # Verifica código"
    echo "  $0 run      # Executa servidor"
}

# Verifica dependências
check_dependencies

# Comando principal
case "${1:-help}" in
    up)
        up
        ;;
    test)
        test
        ;;
    lint)
        lint
        ;;
    format)
        format
        ;;
    run)
        run
        ;;
    debug)
        debug
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        help
        ;;
    *)
        error "Comando inválido: $1"
        help
        exit 1
        ;;
esac
