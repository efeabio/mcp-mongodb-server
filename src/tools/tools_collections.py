from typing import Dict, Any, Optional
import asyncio

# Estas variáveis serão inicializadas pelo server
mongo_connector = None
logger = None
server = None

def initialize_tools_collections(connector, log, srv):
    """Inicializa as dependências para as tools de collections."""
    global mongo_connector, logger, server
    mongo_connector = connector
    logger = log
    server = srv

async def list_collections(database_name: str) -> Dict[str, Any]:
    """
    Lista todas as collections de um database MongoDB.
    """
    try:
        logger.info("Executando tool: list_collections", database=database_name)
        loop = asyncio.get_event_loop()
        db = mongo_connector.client[database_name]
        collections = await loop.run_in_executor(
            mongo_connector._executor,
            db.list_collection_names
        )
        return {
            "database_name": database_name,
            "collections": [{"name": name} for name in collections],
            "total_count": len(collections),
            "status": "success"
        }
    except Exception as e:
        logger.error("Erro ao listar collections", error=str(e))
        return {
            "error": f"Erro ao listar collections: {str(e)}",
            "status": "error"
        }

async def create_collection(database_name: str, collection_name: str) -> Dict[str, Any]:
    """
    Cria uma nova collection em qualquer database.
    """
    try:
        logger.info("Executando tool: create_collection", database=database_name, collection=collection_name)
        loop = asyncio.get_event_loop()
        db = mongo_connector.client[database_name]
        await loop.run_in_executor(
            mongo_connector._executor,
            lambda: db.create_collection(collection_name)
        )
        return {
            "message": f"Collection '{collection_name}' criada com sucesso.",
            "status": "success"
        }
    except Exception as e:
        logger.error("Erro ao criar collection", error=str(e))
        return {
            "error": f"Erro ao criar collection: {str(e)}",
            "status": "error"
        }

async def drop_collection(database_name: str, collection_name: str) -> Dict[str, Any]:
    """
    Remove uma collection de qualquer database.
    """
    try:
        logger.info("Executando tool: drop_collection", database=database_name, collection=collection_name)
        loop = asyncio.get_event_loop()
        db = mongo_connector.client[database_name]
        await loop.run_in_executor(
            mongo_connector._executor,
            lambda: db.drop_collection(collection_name)
        )
        return {
            "message": f"Collection '{collection_name}' removida com sucesso.",
            "status": "success"
        }
    except Exception as e:
        logger.error("Erro ao remover collection", error=str(e))
        return {
            "error": f"Erro ao remover collection: {str(e)}",
            "status": "error"
        }

async def rename_collection(database_name: str, old_name: str, new_name: str) -> Dict[str, Any]:
    """
    Renomeia uma collection em qualquer database.
    """
    try:
        logger.info("Executando tool: rename_collection", database=database_name, old_name=old_name, new_name=new_name)
        loop = asyncio.get_event_loop()
        db = mongo_connector.client[database_name]
        await loop.run_in_executor(
            mongo_connector._executor,
            lambda: db[old_name].rename(new_name)
        )
        return {
            "message": f"Collection '{old_name}' renomeada para '{new_name}' com sucesso.",
            "status": "success"
        }
    except Exception as e:
        logger.error("Erro ao renomear collection", error=str(e))
        return {
            "error": f"Erro ao renomear collection: {str(e)}",
            "status": "error"
        }

async def validate_collection(database_name: str, collection_name: str) -> Dict[str, Any]:
    """
    Roda validação de integridade em uma collection de qualquer database.
    """
    try:
        logger.info("Executando tool: validate_collection", database=database_name, collection=collection_name)
        loop = asyncio.get_event_loop()
        db = mongo_connector.client[database_name]
        result = await loop.run_in_executor(
            mongo_connector._executor,
            lambda: db.command({"validate": collection_name})
        )
        filtered = {k: v for k, v in result.items() if k in ("ok", "ns", "valid", "warnings", "errors")}
        return {
            "result": filtered,
            "status": "success"
        }
    except Exception as e:
        logger.error("Erro ao validar collection", error=str(e))
        return {
            "error": f"Erro ao validar collection: {str(e)}",
            "status": "error"
        }

async def count_documents(database_name: str, collection_name: str, filter: Optional[dict] = None) -> Dict[str, Any]:
    """
    Conta quantos documentos existem em uma collection de qualquer database.
    """
    try:
        logger.info("Executando tool: count_documents", database=database_name, collection=collection_name, filter=filter)
        loop = asyncio.get_event_loop()
        db = mongo_connector.client[database_name]
        collection = db[collection_name]
        count = await loop.run_in_executor(
            mongo_connector._executor,
            lambda: collection.count_documents(filter or {})
        )
        return {
            "count": count,
            "status": "success"
        }
    except Exception as e:
        logger.error("Erro ao contar documentos", error=str(e))
        return {
            "error": f"Erro ao contar documentos: {str(e)}",
            "status": "error"
        }

async def aggregate(database_name: str, collection_name: str, pipeline: list) -> Dict[str, Any]:
    """
    Executa um pipeline de agregação customizada em qualquer collection de qualquer database.
    """
    try:
        logger.info("Executando tool: aggregate", database=database_name, collection=collection_name, pipeline=pipeline)
        loop = asyncio.get_event_loop()
        db = mongo_connector.client[database_name]
        collection = db[collection_name]
        result = await loop.run_in_executor(
            mongo_connector._executor,
            lambda: list(collection.aggregate(pipeline))
        )
        return {
            "result": result,
            "count": len(result),
            "status": "success"
        }
    except Exception as e:
        logger.error("Erro ao executar agregação", error=str(e))
        return {
            "error": f"Erro ao executar agregação: {str(e)}",
            "status": "error"
        } 