"""
Configuração de logging estruturado para o FastMCP MongoDB Server.

Este módulo configura o logging estruturado usando structlog
para melhor observabilidade e debugging.
"""

import structlog
import logging
from typing import Optional


def setup_logging(level: str = "INFO") -> None:
    """
    Configura logging estruturado.
    
    Args:
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Configura logging padrão
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, level.upper())
    )
    
    # Configura structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Retorna logger configurado.
    
    Args:
        name: Nome do logger (geralmente __name__)
        
    Returns:
        Logger configurado com structlog
    """
    return structlog.get_logger(name)


def configure_logging_for_tests() -> None:
    """
    Configura logging para testes.
    
    Configura logging em modo mais simples para testes,
    sem JSON rendering para facilitar debugging.
    """
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


# Configuração inicial do logging
setup_logging() 