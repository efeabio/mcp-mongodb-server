from typing import Dict, Any
import asyncio

# Estas variáveis serão inicializadas pelo server
mongo_connector = None
logger = None
server = None

def initialize_tools_stats(connector, log, srv):
    """Inicializa as dependências para as tools de estatísticas."""
    global mongo_connector, logger, server
    mongo_connector = connector
    logger = log
    server = srv

async def get_server_status() -> Dict[str, Any]:
    """
    Retorna o status atual do servidor MongoDB.
    """
    try:
        logger.info("Executando tool: get_server_status")
        loop = asyncio.get_event_loop()
        status = await loop.run_in_executor(
            mongo_connector._executor,
            lambda: mongo_connector.client.admin.command("serverStatus")
        )
        
        # Filtra apenas informações relevantes
        filtered_status = {
            "version": status.get("version"),
            "uptime": status.get("uptime"),
            "connections": status.get("connections", {}),
            "opcounters": status.get("opcounters", {}),
            "mem": status.get("mem", {}),
            "ok": status.get("ok")
        }
        
        return {
            "status": filtered_status,
            "status_code": "success"
        }
    except Exception as e:
        logger.error("Erro ao obter status do servidor", error=str(e))
        return {
            "error": f"Erro ao obter status do servidor: {str(e)}",
            "status": "error"
        }

async def get_system_stats() -> Dict[str, Any]:
    """
    Retorna estatísticas do sistema.
    """
    try:
        logger.info("Executando tool: get_system_stats")
        loop = asyncio.get_event_loop()
        stats = await loop.run_in_executor(
            mongo_connector._executor,
            lambda: mongo_connector.client.admin.command("dbStats")
        )
        
        return {
            "system_stats": stats,
            "status": "success"
        }
    except Exception as e:
        logger.error("Erro ao obter estatísticas do sistema", error=str(e))
        return {
            "error": f"Erro ao obter estatísticas do sistema: {str(e)}",
            "status": "error"
        } 