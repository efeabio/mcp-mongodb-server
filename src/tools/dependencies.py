"""
Dependências compartilhadas para as tools do MongoDB.
Este arquivo evita importações circulares entre server.py e os módulos de tools.
"""

from src.utils.mongo_connector import MongoDBConnector
from src.utils.logger import get_logger

# Instâncias globais que serão inicializadas pelo server
mongo_connector = None
logger = None

def initialize_dependencies(connector: MongoDBConnector, log):
    """Inicializa as dependências compartilhadas."""
    global mongo_connector, logger
    mongo_connector = connector
    logger = log

# O server será importado dinamicamente quando necessário
def get_server():
    """Retorna a instância do server de forma dinâmica para evitar importação circular."""
    from src.server import server
    return server 