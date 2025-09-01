from typing import Dict, Any
import asyncio
from src.tools.connection_guard import require_connection
from src.tools.tools_connection import get_mongo_connector

# Estas variáveis serão inicializadas pelo server
mongo_connector = None
logger = None
server = None

def initialize_tools_databases(connector, log, srv):
    """Inicializa as dependências para as tools de databases."""
    global mongo_connector, logger, server
    mongo_connector = connector
    logger = log
    server = srv

def get_connector():
    """Obtém o conector MongoDB atual."""
    return get_mongo_connector() or mongo_connector

@require_connection
async def list_databases() -> Dict[str, Any]:
    """
    Lista todos os databases disponíveis no MongoDB.
    """
    try:
        logger.info("Executando tool: list_databases")
        connector = get_connector()
        loop = asyncio.get_event_loop()
        databases = await loop.run_in_executor(
            connector._executor,
            connector.client.list_database_names
        )
        
        # Filtra databases do sistema
        user_databases = [name for name in databases if name not in ['admin', 'local', 'config']]
        
        return {
            "databases": [{"name": name} for name in user_databases],
            "total_count": len(user_databases),
            "status": "success"
        }
    except Exception as e:
        logger.error("Erro ao listar databases", error=str(e))
        return {
            "error": f"Erro ao listar databases: {str(e)}",
            "status": "error"
        }

@require_connection
async def drop_database(database_name: str) -> Dict[str, Any]:
    """
    Remove um database completamente.
    """
    try:
        logger.info("Executando tool: drop_database", database=database_name)
        connector = get_connector()
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            connector._executor,
            lambda: connector.client.drop_database(database_name)
        )
        return {
            "message": f"Database '{database_name}' removido com sucesso.",
            "status": "success"
        }
    except Exception as e:
        logger.error("Erro ao remover database", error=str(e))
        return {
            "error": f"Erro ao remover database: {str(e)}",
            "status": "error"
        }

@require_connection
async def get_database_info(database_name: str) -> Dict[str, Any]:
    """
    Retorna informações detalhadas de um database MongoDB.
    """
    try:
        logger.info("Executando tool: get_database_info", database=database_name)
        connector = get_connector()
        loop = asyncio.get_event_loop()
        db = connector.client[database_name]
        stats = await loop.run_in_executor(
            connector._executor,
            lambda: db.command("dbStats")
        )
        
        return {
            "database": {
                "name": database_name,
                "size_on_disk": stats.get("dataSize", 0),
                "collections": stats.get("collections", 0),
                "objects": stats.get("objects", 0),
                "avg_obj_size": stats.get("avgObjSize", 0),
                "data_size": stats.get("dataSize", 0),
                "storage_size": stats.get("storageSize", 0),
                "indexes": stats.get("indexes", 0),
                "index_size": stats.get("indexSize", 0)
            },
            "status": "success"
        }
    except Exception as e:
        logger.error("Erro ao obter informações do database", error=str(e))
        return {
            "error": f"Erro ao obter informações do database: {str(e)}",
            "status": "error"
        } 