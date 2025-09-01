"""
Servidor FastMCP para MongoDB
"""

from typing import Dict, Any, Optional, List
import logging
from concurrent.futures import ThreadPoolExecutor

from fastmcp import FastMCP
from src.utils.logger import get_logger

# Configuração do logging
logging.basicConfig(level=logging.INFO)

# Criação do servidor FastMCP
server = FastMCP("mongodb-info-server")

# Inicialização do conector MongoDB (será configurado dinamicamente)
mongo_connector = None

# Logger
logger = get_logger(__name__)

# Importação e inicialização das tools
def initialize_tools():
    """Inicializa todas as tools e suas dependências."""
    # Importa os módulos de tools para que os decorators sejam executados
    from src.tools import tools_documents, tools_collections, tools_indexes, tools_databases, tools_stats, tools_connection
    from src.tools.decorators import register_tools_with_server
    from src.tools.dependencies import DependencyContainer
    
    # Inicializa o DependencyContainer com o servidor
    DependencyContainer.initialize(mongo_connector, logger, server)
    
    # Inicializa as dependências de cada módulo (para compatibilidade)
    tools_connection.initialize_tools_connection(mongo_connector, logger, server)
    tools_documents.initialize_tools_documents(mongo_connector, logger, server)
    tools_collections.initialize_tools_collections(mongo_connector, logger, server)
    tools_indexes.initialize_tools_indexes(mongo_connector, logger, server)
    tools_databases.initialize_tools_databases(mongo_connector, logger, server)
    tools_stats.initialize_tools_stats(mongo_connector, logger, server)
    
    # Registra todas as tools automaticamente usando o sistema de decorators
    register_tools_with_server()
    
    # Registra tools que ainda não foram migradas para o sistema de decorators
    # Tools de documentos
    @server.tool()
    async def mongodb_list_documents(database_name: str, collection_name: str, limit: int = 20):
        return await tools_documents.list_documents(database_name, collection_name, limit)
    
    @server.tool()
    async def mongodb_get_document(database_name: str, collection_name: str, field: str, value: str):
        return await tools_documents.get_document(database_name, collection_name, field, value)
    
    @server.tool()
    async def mongodb_insert_document(database_name: str, collection_name: str, document: dict):
        return await tools_documents.insert_document(database_name, collection_name, document)
    
    @server.tool()
    async def mongodb_update_document(database_name: str, collection_name: str, field: str, value: str, update: dict):
        return await tools_documents.update_document(database_name, collection_name, field, value, update)
    
    @server.tool()
    async def mongodb_delete_document(database_name: str, collection_name: str, field: str, value: str):
        return await tools_documents.delete_document(database_name, collection_name, field, value)
    
    # Tools de coleções
    @server.tool()
    async def mongodb_list_collections(database_name: str):
        return await tools_collections.list_collections(database_name)
    
    @server.tool()
    async def mongodb_create_collection(database_name: str, collection_name: str):
        return await tools_collections.create_collection(database_name, collection_name)
    
    @server.tool()
    async def mongodb_drop_collection(database_name: str, collection_name: str):
        return await tools_collections.drop_collection(database_name, collection_name)
    
    @server.tool()
    async def mongodb_get_collection_info(database_name: str, collection_name: str):
        return await tools_collections.get_collection_info(database_name, collection_name)
    
    # Tools de databases
    @server.tool()
    async def mongodb_list_databases():
        return await tools_databases.list_databases()
    
    @server.tool()
    async def mongodb_get_database_info(database_name: str):
        return await tools_databases.get_database_info(database_name)
    
    @server.tool()
    async def mongodb_create_database(database_name: str):
        return await tools_databases.create_database(database_name)
    
    @server.tool()
    async def mongodb_drop_database(database_name: str):
        return await tools_databases.drop_database(database_name)
    
    # Tools de indexes
    @server.tool()
    async def mongodb_list_indexes(database_name: str, collection_name: str):
        return await tools_indexes.list_indexes(database_name, collection_name)
    
    @server.tool()
    async def mongodb_create_index(database_name: str, collection_name: str, index_spec: dict, index_options: dict = None):
        return await tools_indexes.create_index(database_name, collection_name, index_spec, index_options)
    
    @server.tool()
    async def mongodb_drop_index(database_name: str, collection_name: str, index_name: str):
        return await tools_indexes.drop_index(database_name, collection_name, index_name)
    
    # Tools de estatísticas
    @server.tool()
    async def mongodb_get_server_status():
        return await tools_stats.get_server_status()
    
    @server.tool()
    async def mongodb_get_system_stats():
        return await tools_stats.get_system_stats()

# Funções de tools para compatibilidade com testes
async def list_databases():
    """Lista todos os databases."""
    try:
        from src.tools import tools_databases
        return await tools_databases.list_databases()
    except Exception as e:
        return {"status": "error", "error": f"Erro ao listar databases: {str(e)}"}

async def get_database_info(database_name: str):
    """Obtém informações de um database."""
    try:
        from src.tools import tools_databases
        return await tools_databases.get_database_info(database_name)
    except Exception as e:
        return {"status": "error", "error": f"Erro ao obter informações do database: {str(e)}"}

async def list_collections(database_name: str):
    """Lista collections de um database."""
    try:
        from src.tools import tools_collections
        return await tools_collections.list_collections(database_name)
    except Exception as e:
        return {"status": "error", "error": f"Erro ao listar collections: {str(e)}"}

async def get_collection_info(database_name: str, collection_name: str):
    """Obtém informações de uma collection."""
    try:
        from src.tools import tools_collections
        return await tools_collections.validate_collection(database_name, collection_name)
    except Exception as e:
        return {"status": "error", "error": f"Erro ao obter informações da collection: {str(e)}"}

async def get_server_status():
    """Obtém status do servidor."""
    try:
        from src.tools import tools_stats
        return await tools_stats.get_server_status()
    except Exception as e:
        return {"status": "error", "error": f"Erro ao obter status do servidor: {str(e)}"}

async def get_system_stats():
    """Obtém estatísticas do sistema."""
    try:
        from src.tools import tools_stats
        return await tools_stats.get_system_stats()
    except Exception as e:
        return {"status": "error", "error": f"Erro ao obter estatísticas do sistema: {str(e)}"}

# Inicializa as tools
initialize_tools()

# Função para limpeza de recursos
def cleanup():
    """
    Função para limpeza de recursos do servidor.
    """
    try:
        if mongo_connector:
            mongo_connector.close()
        logger.info("Recursos do servidor limpos com sucesso")
    except Exception as e:
        logger.error("Erro ao limpar recursos", error=str(e))

# Registra função de limpeza
import atexit
atexit.register(cleanup) 