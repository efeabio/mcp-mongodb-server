"""
Configurações do FastMCP MongoDB Server.

Este módulo contém todas as configurações do projeto usando Pydantic
para validação e tipagem forte.
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Configurações do FastMCP MongoDB Server.
    
    Atributos:
        mongodb_uri: URI de conexão com MongoDB
        mongodb_username: Usuário do MongoDB (opcional)
        mongodb_password: Senha do MongoDB (opcional)
        mongodb_auth_source: Database de autenticação
        fastmcp_server_name: Nome do servidor FastMCP
        fastmcp_server_version: Versão do servidor
        fastmcp_server_description: Descrição do servidor
        log_level: Nível de logging
        connection_timeout: Timeout de conexão em ms
        query_timeout: Timeout de query em ms
        max_connections: Número máximo de conexões
    """
    
    # MongoDB Configuration
    mongodb_uri: str = Field(
        default="mongodb://localhost:27017",
        description="URI de conexão com MongoDB"
    )
    mongodb_username: Optional[str] = Field(
        default=None,
        description="Usuário do MongoDB"
    )
    mongodb_password: Optional[str] = Field(
        default=None,
        description="Senha do MongoDB"
    )
    mongodb_auth_source: str = Field(
        default="admin",
        description="Database de autenticação"
    )
    
    # FastMCP Server Configuration
    fastmcp_server_name: str = Field(
        default="mongodb-info-server",
        description="Nome do servidor FastMCP"
    )
    fastmcp_server_version: str = Field(
        default="1.0.0",
        description="Versão do servidor"
    )
    fastmcp_server_description: str = Field(
        default="FastMCP Server for MongoDB information and statistics",
        description="Descrição do servidor"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        description="Nível de logging"
    )
    
    # Performance
    connection_timeout: int = Field(
        default=5000,
        description="Timeout de conexão em milissegundos"
    )
    query_timeout: int = Field(
        default=30000,
        description="Timeout de query em milissegundos"
    )
    max_connections: int = Field(
        default=10,
        description="Número máximo de conexões"
    )
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """
        Valida o nível de logging.
        
        Args:
            v: Nível de logging
            
        Returns:
            Nível de logging validado
            
        Raises:
            ValueError: Se o nível de logging for inválido
        """
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Nível de logging inválido: {v}")
        return v.upper()
    
    @field_validator('connection_timeout', 'query_timeout')
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        """
        Valida timeout de conexão e query.
        
        Args:
            v: Valor do timeout
            
        Returns:
            Timeout validado
            
        Raises:
            ValueError: Se o timeout for inválido
        """
        if v <= 0:
            raise ValueError("Timeout deve ser maior que zero")
        return v
    
    @field_validator('max_connections')
    @classmethod
    def validate_max_connections(cls, v: int) -> int:
        """
        Valida número máximo de conexões.
        
        Args:
            v: Número máximo de conexões
            
        Returns:
            Número máximo de conexões validado
            
        Raises:
            ValueError: Se o número de conexões for inválido
        """
        if v <= 0 or v > 100:
            raise ValueError("Número máximo de conexões deve estar entre 1 e 100")
        return v
    
    model_config = {
        "case_sensitive": False,
        "extra": "ignore"
    }


# Instância global das configurações
settings = Settings() 