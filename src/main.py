"""
Ponto de entrada da aplicação FastMCP MongoDB Server.

Este módulo inicia o servidor FastMCP em modo STDIO.
"""

import sys
from src.server import server
from src.utils.logger import get_logger
from src.config.settings import settings


def main():
    """
    Função principal da aplicação.
    
    Inicia o servidor FastMCP em modo STDIO.
    """
    logger = get_logger(__name__)
    
    try:
        logger.info("Iniciando FastMCP MongoDB Server", 
                   version=settings.fastmcp_server_version,
                   name=settings.fastmcp_server_name)
        
        # Executa o servidor em modo STDIO
        server.run()
        
    except KeyboardInterrupt:
        logger.info("Servidor interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.error("Erro fatal no servidor", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main() 