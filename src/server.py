"""
Servidor FastMCP para MongoDB.

Este módulo contém o servidor FastMCP principal que disponibiliza
informações de um servidor MongoDB através do Model Context Protocol.
"""

from mcp.server import FastMCP
from typing import Any, Dict, List, Optional
from src.utils.mongo_connector import MongoDBConnector
from src.utils.logger import get_logger
from src.services.database_service import DatabaseService
from src.services.collection_service import CollectionService
from src.services.stats_service import StatsService
from src.config.settings import settings
from src.core.exceptions import (
    MongoDBConnectionError,
    DatabaseNotFoundError,
    CollectionNotFoundError
)
from urllib.parse import quote_plus

# Criação do servidor FastMCP
server = FastMCP(settings.fastmcp_server_name)

# Monta a URI de conexão com autenticação, se necessário
def build_mongodb_uri():
    uri = settings.mongodb_uri
    username = settings.mongodb_username
    password = settings.mongodb_password
    auth_source = settings.mongodb_auth_source
    
    if username and password:
        # Remove protocolo e host da URI base
        if uri.startswith("mongodb://"):
            uri_base = uri[len("mongodb://"):]
        else:
            uri_base = uri
        # Monta URI com usuário, senha e authSource
        uri = f"mongodb://{quote_plus(username)}:{quote_plus(password)}@{uri_base}"
        if auth_source:
            if "/?" in uri:
                uri += f"&authSource={auth_source}"
            else:
                uri += f"/?authSource={auth_source}"
    return uri

# Inicialização do conector MongoDB
mongo_connector = MongoDBConnector(
    uri=build_mongodb_uri(),
    max_pool_size=settings.max_connections
)

# Inicialização dos serviços
database_service = DatabaseService(mongo_connector)
collection_service = CollectionService(mongo_connector)
stats_service = StatsService(mongo_connector)

# Logger
logger = get_logger(__name__)

# DEBUG: Exibe variáveis de conexão MongoDB (exceto senha)
print("DEBUG - Variáveis de conexão MongoDB:")
print("MONGODB_URI:", settings.mongodb_uri)
print("MONGODB_USERNAME:", settings.mongodb_username)
print("MONGODB_AUTH_SOURCE:", settings.mongodb_auth_source)
print("MAX_CONNECTIONS:", settings.max_connections)

# Importação e inicialização das tools
def initialize_tools():
    """Inicializa todas as tools e suas dependências."""
    # Importa os módulos de tools
    from src.tools import tools_documents, tools_collections, tools_indexes, tools_databases, tools_stats
    
    # Inicializa as dependências de cada módulo
    tools_documents.initialize_tools_documents(mongo_connector, logger, server)
    tools_collections.initialize_tools_collections(mongo_connector, logger, server)
    tools_indexes.initialize_tools_indexes(mongo_connector, logger, server)
    tools_databases.initialize_tools_databases(mongo_connector, logger, server)
    tools_stats.initialize_tools_stats(mongo_connector, logger, server)
    
    # Registra as tools no server
    @server.tool()
    async def list_documents(database_name: str, collection_name: str, limit: int = 20):
        return await tools_documents.list_documents(database_name, collection_name, limit)
    
    @server.tool()
    async def get_document(database_name: str, collection_name: str, field: str, value: str):
        return await tools_documents.get_document(database_name, collection_name, field, value)
    
    @server.tool()
    async def insert_document(database_name: str, collection_name: str, document: dict):
        return await tools_documents.insert_document(database_name, collection_name, document)
    
    @server.tool()
    async def update_document(database_name: str, collection_name: str, field: str, value: str, update: dict):
        return await tools_documents.update_document(database_name, collection_name, field, value, update)
    
    @server.tool()
    async def delete_document(database_name: str, collection_name: str, field: str, value: str):
        return await tools_documents.delete_document(database_name, collection_name, field, value)
    
    @server.tool()
    async def list_collections(database_name: str):
        return await tools_collections.list_collections(database_name)
    
    @server.tool()
    async def create_collection(database_name: str, collection_name: str):
        return await tools_collections.create_collection(database_name, collection_name)
    
    @server.tool()
    async def drop_collection(database_name: str, collection_name: str):
        return await tools_collections.drop_collection(database_name, collection_name)
    
    @server.tool()
    async def rename_collection(database_name: str, old_name: str, new_name: str):
        return await tools_collections.rename_collection(database_name, old_name, new_name)
    
    @server.tool()
    async def validate_collection(database_name: str, collection_name: str):
        return await tools_collections.validate_collection(database_name, collection_name)
    
    @server.tool()
    async def count_documents(database_name: str, collection_name: str, filter: Optional[dict] = None):
        return await tools_collections.count_documents(database_name, collection_name, filter)
    
    @server.tool()
    async def aggregate(database_name: str, collection_name: str, pipeline: list):
        return await tools_collections.aggregate(database_name, collection_name, pipeline)
    
    @server.tool()
    async def list_databases():
        return await tools_databases.list_databases()
    
    @server.tool()
    async def drop_database(database_name: str):
        return await tools_databases.drop_database(database_name)
    
    @server.tool()
    async def create_index(database_name: str, collection_name: str, keys: list, index_name: Optional[str] = None, unique: bool = False):
        return await tools_indexes.create_index(database_name, collection_name, keys, index_name, unique)
    
    @server.tool()
    async def list_indexes(database_name: str, collection_name: str):
        return await tools_indexes.list_indexes(database_name, collection_name)
    
    @server.tool()
    async def drop_index(database_name: str, collection_name: str, index_name: str):
        return await tools_indexes.drop_index(database_name, collection_name, index_name)
    
    @server.tool()
    async def get_database_info(database_name: str):
        return await tools_databases.get_database_info(database_name)
    
    @server.tool()
    async def get_server_status():
        return await tools_stats.get_server_status()
    
    @server.tool()
    async def get_system_stats():
        return await tools_stats.get_system_stats()

# Inicializa as tools
initialize_tools()

# Função para limpeza de recursos
def cleanup():
    """
    Função para limpeza de recursos do servidor.
    """
    try:
        mongo_connector.close()
        logger.info("Recursos do servidor limpos com sucesso")
    except Exception as e:
        logger.error("Erro ao limpar recursos", error=str(e))

# Registra função de limpeza
import atexit
atexit.register(cleanup) 