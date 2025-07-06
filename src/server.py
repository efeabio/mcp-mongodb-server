"""
Servidor FastMCP para MongoDB.

Este módulo contém o servidor FastMCP principal que disponibiliza
informações de um servidor MongoDB através do Model Context Protocol.
"""

from mcp.server import FastMCP
from typing import Any, Dict, List
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


# Criação do servidor FastMCP
server = FastMCP(settings.fastmcp_server_name)

# Inicialização do conector MongoDB
mongo_connector = MongoDBConnector(
    uri=settings.mongodb_uri,
    max_pool_size=settings.max_connections
)

# Inicialização dos serviços
database_service = DatabaseService(mongo_connector)
collection_service = CollectionService(mongo_connector)
stats_service = StatsService(mongo_connector)

# Logger
logger = get_logger(__name__)


@server.tool()
async def list_databases() -> Dict[str, Any]:
    """
    Lista todos os databases disponíveis no MongoDB.
    
    Returns:
        Dicionário com lista de databases e suas informações básicas
    """
    try:
        logger.info("Executando tool: list_databases")
        databases = await database_service.list_databases()
        
        return {
            "databases": databases,
            "total_count": len(databases),
            "status": "success"
        }
    except Exception as e:
        logger.error("Erro ao listar databases", error=str(e))
        return {
            "error": f"Erro ao listar databases: {str(e)}",
            "status": "error"
        }


@server.tool()
async def get_database_info(database_name: str) -> Dict[str, Any]:
    """
    Retorna informações detalhadas de um database MongoDB.
    
    Args:
        database_name: Nome do database
        
    Returns:
        Dicionário com informações detalhadas do database
    """
    try:
        logger.info("Executando tool: get_database_info", database=database_name)
        db_info = await database_service.get_database_info(database_name)
        
        return {
            "database": {
                "name": db_info.name,
                "size_on_disk": db_info.size_on_disk,
                "collections": db_info.collections,
                "objects": db_info.objects,
                "avg_obj_size": db_info.avg_obj_size,
                "data_size": db_info.data_size,
                "storage_size": db_info.storage_size,
                "indexes": db_info.indexes,
                "index_size": db_info.index_size
            },
            "status": "success"
        }
    except ValueError as e:
        logger.error("Erro de validação ao obter informações do database", 
                    database=database_name, error=str(e))
        return {
            "error": f"Erro de validação: {str(e)}",
            "status": "error"
        }
    except DatabaseNotFoundError as e:
        logger.error("Database não encontrado", database=database_name, error=str(e))
        return {
            "error": f"Database não encontrado: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        logger.error("Erro ao obter informações do database", 
                    database=database_name, error=str(e))
        return {
            "error": f"Erro ao obter informações do database: {str(e)}",
            "status": "error"
        }


@server.tool()
async def list_collections(database_name: str) -> Dict[str, Any]:
    """
    Lista todas as collections de um database MongoDB.
    
    Args:
        database_name: Nome do database
        
    Returns:
        Dicionário com lista de collections e suas informações
    """
    try:
        logger.info("Executando tool: list_collections", database=database_name)
        collections = await collection_service.list_collections(database_name)
        
        return {
            "database_name": database_name,
            "collections": collections,
            "total_count": len(collections),
            "status": "success"
        }
    except ValueError as e:
        logger.error("Erro de validação ao listar collections", 
                    database=database_name, error=str(e))
        return {
            "error": f"Erro de validação: {str(e)}",
            "status": "error"
        }
    except DatabaseNotFoundError as e:
        logger.error("Database não encontrado", database=database_name, error=str(e))
        return {
            "error": f"Database não encontrado: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        logger.error("Erro ao listar collections", 
                    database=database_name, error=str(e))
        return {
            "error": f"Erro ao listar collections: {str(e)}",
            "status": "error"
        }


@server.tool()
async def get_collection_info(database_name: str, collection_name: str) -> Dict[str, Any]:
    """
    Retorna informações detalhadas de uma collection MongoDB.
    
    Args:
        database_name: Nome do database
        collection_name: Nome da collection
        
    Returns:
        Dicionário com informações detalhadas da collection
    """
    try:
        logger.info("Executando tool: get_collection_info", 
                   database=database_name, collection=collection_name)
        collection_info = await collection_service.get_collection_info(
            database_name, collection_name
        )
        
        return {
            "collection": {
                "name": collection_info.name,
                "count": collection_info.count,
                "size": collection_info.size,
                "avg_obj_size": collection_info.avg_obj_size,
                "storage_size": collection_info.storage_size,
                "total_index_size": collection_info.total_index_size,
                "indexes": collection_info.indexes
            },
            "database_name": database_name,
            "status": "success"
        }
    except ValueError as e:
        logger.error("Erro de validação ao obter informações da collection", 
                    database=database_name, collection=collection_name, error=str(e))
        return {
            "error": f"Erro de validação: {str(e)}",
            "status": "error"
        }
    except DatabaseNotFoundError as e:
        logger.error("Database não encontrado", 
                    database=database_name, collection=collection_name, error=str(e))
        return {
            "error": f"Database não encontrado: {str(e)}",
            "status": "error"
        }
    except CollectionNotFoundError as e:
        logger.error("Collection não encontrada", 
                    database=database_name, collection=collection_name, error=str(e))
        return {
            "error": f"Collection não encontrada: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        logger.error("Erro ao obter informações da collection", 
                    database=database_name, collection=collection_name, error=str(e))
        return {
            "error": f"Erro ao obter informações da collection: {str(e)}",
            "status": "error"
        }


@server.tool()
async def get_server_status() -> Dict[str, Any]:
    """
    Retorna status geral do servidor MongoDB.
    
    Returns:
        Dicionário com status detalhado do servidor
    """
    try:
        logger.info("Executando tool: get_server_status")
        server_status = await stats_service.get_server_status()
        
        return {
            "server_status": {
                "version": server_status.version,
                "uptime": server_status.uptime,
                "connections": server_status.connections,
                "memory": server_status.memory,
                "operations": server_status.operations,
                "network": server_status.network
            },
            "status": "success"
        }
    except Exception as e:
        logger.error("Erro ao obter status do servidor", error=str(e))
        return {
            "error": f"Erro ao obter status do servidor: {str(e)}",
            "status": "error"
        }


@server.tool()
async def get_system_stats() -> Dict[str, Any]:
    """
    Retorna estatísticas do sistema.
    
    Returns:
        Dicionário com estatísticas detalhadas do sistema
    """
    try:
        logger.info("Executando tool: get_system_stats")
        system_stats = await stats_service.get_system_stats()
        
        return {
            "system_stats": system_stats,
            "status": "success"
        }
    except Exception as e:
        logger.error("Erro ao obter estatísticas do sistema", error=str(e))
        return {
            "error": f"Erro ao obter estatísticas do sistema: {str(e)}",
            "status": "error"
        }


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