from typing import Dict, Any
import asyncio

# Estas variáveis serão inicializadas pelo server
mongo_connector = None
logger = None
server = None

def initialize_tools_documents(connector, log, srv):
    """Inicializa as dependências para as tools de documentos."""
    global mongo_connector, logger, server
    mongo_connector = connector
    logger = log
    server = srv

async def list_documents(database_name: str, collection_name: str, limit: int = 20) -> Dict[str, Any]:
    """
    Lista documentos de qualquer collection de qualquer database.
    
    Args:
        database_name: Nome do banco
        collection_name: Nome da collection
        limit: Quantidade máxima de documentos a retornar (padrão: 20)
    
    Returns:
        Dicionário com a lista de documentos
    """
    try:
        logger.info("Executando tool: list_documents", database=database_name, collection=collection_name, limit=limit)
        loop = asyncio.get_event_loop()
        db = mongo_connector.client[database_name]
        collection = db[collection_name]
        documents = await loop.run_in_executor(
            mongo_connector._executor,
            lambda: list(collection.find({}, {"_id": 0}).limit(limit))
        )
        return {
            "documents": documents,
            "count": len(documents),
            "status": "success"
        }
    except Exception as e:
        logger.error("Erro ao listar documentos", error=str(e))
        return {
            "error": f"Erro ao listar documentos: {str(e)}",
            "status": "error"
        }

async def get_document(database_name: str, collection_name: str, field: str, value: str) -> Dict[str, Any]:
    """
    Busca um documento em qualquer collection de qualquer database por um campo e valor.
    
    Args:
        database_name: Nome do banco
        collection_name: Nome da collection
        field: Campo para busca
        value: Valor do campo
    
    Returns:
        Dicionário com o documento encontrado (ou mensagem de não encontrado)
    """
    try:
        logger.info("Executando tool: get_document", database=database_name, collection=collection_name, field=field, value=value)
        loop = asyncio.get_event_loop()
        db = mongo_connector.client[database_name]
        collection = db[collection_name]
        document = await loop.run_in_executor(
            mongo_connector._executor,
            lambda: collection.find_one({field: value}, {"_id": 0})
        )
        if document:
            return {
                "document": document,
                "status": "success"
            }
        else:
            return {
                "error": "Documento não encontrado.",
                "status": "not_found"
            }
    except Exception as e:
        logger.error("Erro ao buscar documento", error=str(e))
        return {
            "error": f"Erro ao buscar documento: {str(e)}",
            "status": "error"
        }

async def insert_document(database_name: str, collection_name: str, document: dict) -> Dict[str, Any]:
    """
    Insere um novo documento em qualquer collection de qualquer database.
    
    Args:
        database_name: Nome do banco
        collection_name: Nome da collection
        document: Dicionário com os dados do documento a ser inserido
    
    Returns:
        Dicionário com status da operação
    """
    try:
        logger.info("Executando tool: insert_document", database=database_name, collection=collection_name, document=document)
        loop = asyncio.get_event_loop()
        db = mongo_connector.client[database_name]
        collection = db[collection_name]
        result = await loop.run_in_executor(
            mongo_connector._executor,
            lambda: collection.insert_one(document)
        )
        return {
            "inserted_id": str(result.inserted_id),
            "status": "success"
        }
    except Exception as e:
        logger.error("Erro ao inserir documento", error=str(e))
        return {
            "error": f"Erro ao inserir documento: {str(e)}",
            "status": "error"
        }

async def update_document(database_name: str, collection_name: str, field: str, value: str, update: dict) -> Dict[str, Any]:
    """
    Atualiza um documento em qualquer collection de qualquer database, buscando por um campo e valor.
    
    Args:
        database_name: Nome do banco
        collection_name: Nome da collection
        field: Campo para busca
        value: Valor do campo
        update: Dicionário com os campos a serem atualizados
    
    Returns:
        Dicionário com status da operação
    """
    try:
        logger.info("Executando tool: update_document", database=database_name, collection=collection_name, field=field, value=value, update=update)
        loop = asyncio.get_event_loop()
        db = mongo_connector.client[database_name]
        collection = db[collection_name]
        result = await loop.run_in_executor(
            mongo_connector._executor,
            lambda: collection.update_one({field: value}, {"$set": update})
        )
        if result.matched_count == 0:
            return {
                "error": "Documento não encontrado para atualização.",
                "status": "not_found"
            }
        return {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "status": "success"
        }
    except Exception as e:
        logger.error("Erro ao atualizar documento", error=str(e))
        return {
            "error": f"Erro ao atualizar documento: {str(e)}",
            "status": "error"
        }

async def delete_document(database_name: str, collection_name: str, field: str, value: str) -> Dict[str, Any]:
    """
    Remove um documento em qualquer collection de qualquer database, buscando por um campo e valor.
    
    Args:
        database_name: Nome do banco
        collection_name: Nome da collection
        field: Campo para busca
        value: Valor do campo
    
    Returns:
        Dicionário com status da operação
    """
    try:
        logger.info("Executando tool: delete_document", database=database_name, collection=collection_name, field=field, value=value)
        loop = asyncio.get_event_loop()
        db = mongo_connector.client[database_name]
        collection = db[collection_name]
        result = await loop.run_in_executor(
            mongo_connector._executor,
            lambda: collection.delete_one({field: value})
        )
        if result.deleted_count == 0:
            return {
                "error": "Documento não encontrado para remoção.",
                "status": "not_found"
            }
        return {
            "deleted_count": result.deleted_count,
            "status": "success"
        }
    except Exception as e:
        logger.error("Erro ao remover documento", error=str(e))
        return {
            "error": f"Erro ao remover documento: {str(e)}",
            "status": "error"
        } 