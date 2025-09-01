#!/bin/bash
# Script para iniciar o servidor MCP MongoDB com conexão dinâmica
# Todas as configurações são feitas via tools de conexão

# Ativa o ambiente virtual e executa o servidor MCP RabbitMQ
cd "$(dirname "$0")"
source venv/bin/activate

# Adiciona o diretório atual ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Inicia o servidor MCP MongoDB
python3 src/main.py 