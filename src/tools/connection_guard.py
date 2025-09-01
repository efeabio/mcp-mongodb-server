"""
Decorator para verificar conexão com MongoDB.

Este módulo contém um decorator que verifica se há uma conexão
ativa com MongoDB antes de executar outras tools.
"""

import functools
from typing import Callable, Any, Dict
from src.tools.tools_connection import is_connected

def require_connection(func: Callable) -> Callable:
    """
    Decorator que verifica se há uma conexão ativa com MongoDB.
    
    Se não houver conexão, retorna um erro informando que é necessário
    configurar a conexão primeiro.
    
    Args:
        func: Função a ser decorada
        
    Returns:
        Função decorada que verifica conexão
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> Dict[str, Any]:
        if not is_connected():
            return {
                "status": "error",
                "error": "Nenhuma conexão ativa com MongoDB. Use 'configure_mongodb_connection' primeiro para configurar a conexão.",
                "required_action": "configure_mongodb_connection",
                "suggestion": "Execute a tool 'configure_mongodb_connection' fornecendo os dados de acesso ao MongoDB (host, port, username, password, etc.)"
            }
        
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            return {
                "status": "error",
                "error": f"Erro ao executar {func.__name__}: {str(e)}"
            }
    
    return wrapper
