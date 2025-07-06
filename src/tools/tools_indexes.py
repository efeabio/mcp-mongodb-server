from typing import Dict, Any, List, Optional
import asyncio

# Estas variáveis serão inicializadas pelo server
mongo_connector = None
logger = None
server = None

def initialize_tools_indexes(connector, log, srv):
    """Inicializa as dependências para as tools de índices."""
    global mongo_connector, logger, server
    mongo_connector = connector
    logger = log
    server = srv

async def list_indexes(database_name: str, collection_name: str) -> Dict[str, Any]:
    """
    Lista os índices de uma collection de qualquer database.
    """
    try:
        logger.info("Executando tool: list_indexes", database=database_name, collection=collection_name)
        loop = asyncio.get_event_loop()
        db = mongo_connector.client[database_name]
        collection = db[collection_name]
        indexes = await loop.run_in_executor(
            mongo_connector._executor,
            lambda: list(collection.list_indexes())
        )
        for idx in indexes:
            idx.pop('_id', None)
        return {
            "indexes": indexes,
            "count": len(indexes),
            "status": "success"
        }
    except Exception as e:
        logger.error("Erro ao listar índices", error=str(e))
        return {
            "error": f"Erro ao listar índices: {str(e)}",
            "status": "error"
        }

async def create_index(database_name: str, collection_name: str, keys: List[tuple], index_name: Optional[str] = None, unique: bool = False) -> Dict[str, Any]:
    """
    Cria um índice em uma collection de qualquer database.
    
    Args:
        database_name: Nome do banco
        collection_name: Nome da collection
        keys: Lista de tuplas (campo, direção) - ex: [("name", 1), ("age", -1)]
        index_name: Nome do índice (opcional)
        unique: Se o índice deve ser único
    """
    try:
        logger.info("Executando tool: create_index", database=database_name, collection=collection_name, keys=keys, unique=unique)
        loop = asyncio.get_event_loop()
        db = mongo_connector.client[database_name]
        collection = db[collection_name]
        
        # Converte lista de tuplas para dicionário
        index_keys = dict(keys)
        
        result = await loop.run_in_executor(
            mongo_connector._executor,
            lambda: collection.create_index(index_keys, name=index_name, unique=unique)
        )
        return {
            "index_name": result,
            "message": f"Índice criado com sucesso: {result}",
            "status": "success"
        }
    except Exception as e:
        logger.error("Erro ao criar índice", error=str(e))
        return {
            "error": f"Erro ao criar índice: {str(e)}",
            "status": "error"
        }

async def drop_index(database_name: str, collection_name: str, index_name: str) -> Dict[str, Any]:
    """
    Remove um índice de uma collection de qualquer database.
    
    Args:
        database_name: Nome do banco
        collection_name: Nome da collection
        index_name: Nome do índice a ser removido
    """
    try:
        logger.info("Executando tool: drop_index", database=database_name, collection=collection_name, index_name=index_name)
        loop = asyncio.get_event_loop()
        db = mongo_connector.client[database_name]
        collection = db[collection_name]
        
        result = await loop.run_in_executor(
            mongo_connector._executor,
            lambda: collection.drop_index(index_name)
        )
        return {
            "message": f"Índice '{index_name}' removido com sucesso.",
            "status": "success"
        }
    except Exception as e:
        logger.error("Erro ao remover índice", error=str(e))
        return {
            "error": f"Erro ao remover índice: {str(e)}",
            "status": "error"
        } 