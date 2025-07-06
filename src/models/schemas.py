"""
Schemas Pydantic para o FastMCP MongoDB Server.

Este módulo contém todos os modelos de dados para validação
e serialização das informações do MongoDB.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any


class DatabaseInfo(BaseModel):
    """
    Informações detalhadas de um database MongoDB.
    
    Atributos:
        name: Nome do database
        size_on_disk: Tamanho em disco em bytes
        collections: Número de collections
        objects: Número total de objetos
        avg_obj_size: Tamanho médio dos objetos em bytes
        data_size: Tamanho dos dados em bytes
        storage_size: Tamanho de armazenamento em bytes
        indexes: Número de índices
        index_size: Tamanho dos índices em bytes
    """
    
    name: str = Field(..., description="Nome do database")
    size_on_disk: int = Field(..., description="Tamanho em disco em bytes")
    collections: int = Field(..., description="Número de collections")
    objects: int = Field(..., description="Número total de objetos")
    avg_obj_size: Optional[float] = Field(None, description="Tamanho médio dos objetos")
    data_size: int = Field(..., description="Tamanho dos dados em bytes")
    storage_size: int = Field(..., description="Tamanho de armazenamento em bytes")
    indexes: int = Field(..., description="Número de índices")
    index_size: int = Field(..., description="Tamanho dos índices em bytes")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        Valida nome do database.
        
        Args:
            v: Nome do database
            
        Returns:
            Nome validado
            
        Raises:
            ValueError: Se o nome for inválido
        """
        if not v or len(v) > 64:
            raise ValueError("Nome do database deve ter entre 1 e 64 caracteres")
        return v


class CollectionInfo(BaseModel):
    """
    Informações detalhadas de uma collection MongoDB.
    
    Atributos:
        name: Nome da collection
        count: Número de documentos
        size: Tamanho em bytes
        avg_obj_size: Tamanho médio dos objetos
        storage_size: Tamanho de armazenamento
        total_index_size: Tamanho total dos índices
        indexes: Lista de índices
    """
    
    name: str = Field(..., description="Nome da collection")
    count: int = Field(..., description="Número de documentos")
    size: int = Field(..., description="Tamanho em bytes")
    avg_obj_size: Optional[float] = Field(None, description="Tamanho médio dos objetos")
    storage_size: int = Field(..., description="Tamanho de armazenamento")
    total_index_size: int = Field(..., description="Tamanho total dos índices")
    indexes: List[Dict[str, Any]] = Field(default_factory=list, description="Lista de índices")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        Valida nome da collection.
        
        Args:
            v: Nome da collection
            
        Returns:
            Nome validado
            
        Raises:
            ValueError: Se o nome for inválido
        """
        if not v or len(v) > 255:
            raise ValueError("Nome da collection deve ter entre 1 e 255 caracteres")
        return v


class ServerStatus(BaseModel):
    """
    Status geral do servidor MongoDB.
    
    Atributos:
        version: Versão do MongoDB
        uptime: Tempo de atividade em segundos
        connections: Informações de conexões
        memory: Informações de memória
        operations: Estatísticas de operações
        network: Estatísticas de rede
    """
    
    version: str = Field(..., description="Versão do MongoDB")
    uptime: int = Field(..., description="Tempo de atividade em segundos")
    connections: Dict[str, Any] = Field(..., description="Informações de conexões")
    memory: Dict[str, Any] = Field(..., description="Informações de memória")
    operations: Dict[str, Any] = Field(..., description="Estatísticas de operações")
    network: Dict[str, Any] = Field(..., description="Estatísticas de rede")


class DatabaseQuery(BaseModel):
    """
    Modelo para validação de queries de database.
    
    Atributos:
        database_name: Nome do database
        limit: Limite de resultados
    """
    
    database_name: str = Field(..., description="Nome do database")
    limit: int = Field(default=100, description="Limite de resultados")
    
    @field_validator('database_name')
    @classmethod
    def validate_database_name(cls, v: str) -> str:
        """
        Valida nome do database.
        
        Args:
            v: Nome do database
            
        Returns:
            Nome validado
            
        Raises:
            ValueError: Se o nome for inválido
        """
        if not v or len(v) > 64:
            raise ValueError("Nome do database deve ter entre 1 e 64 caracteres")
        return v
    
    @field_validator('limit')
    @classmethod
    def validate_limit(cls, v: int) -> int:
        """
        Valida limite de resultados.
        
        Args:
            v: Limite de resultados
            
        Returns:
            Limite validado
            
        Raises:
            ValueError: Se o limite for inválido
        """
        if v <= 0 or v > 1000:
            raise ValueError("Limite deve estar entre 1 e 1000")
        return v


class CollectionQuery(BaseModel):
    """
    Modelo para validação de queries de collection.
    
    Atributos:
        database_name: Nome do database
        collection_name: Nome da collection
        limit: Limite de resultados
    """
    
    database_name: str = Field(..., description="Nome do database")
    collection_name: str = Field(..., description="Nome da collection")
    limit: int = Field(default=100, description="Limite de resultados")
    
    @field_validator('database_name')
    @classmethod
    def validate_database_name(cls, v: str) -> str:
        """
        Valida nome do database.
        
        Args:
            v: Nome do database
            
        Returns:
            Nome validado
            
        Raises:
            ValueError: Se o nome for inválido
        """
        if not v or len(v) > 64:
            raise ValueError("Nome do database deve ter entre 1 e 64 caracteres")
        return v
    
    @field_validator('collection_name')
    @classmethod
    def validate_collection_name(cls, v: str) -> str:
        """
        Valida nome da collection.
        
        Args:
            v: Nome da collection
            
        Returns:
            Nome validado
            
        Raises:
            ValueError: Se o nome for inválido
        """
        if not v or len(v) > 255:
            raise ValueError("Nome da collection deve ter entre 1 e 255 caracteres")
        return v
    
    @field_validator('limit')
    @classmethod
    def validate_limit(cls, v: int) -> int:
        """
        Valida limite de resultados.
        
        Args:
            v: Limite de resultados
            
        Returns:
            Limite validado
            
        Raises:
            ValueError: Se o limite for inválido
        """
        if v <= 0 or v > 1000:
            raise ValueError("Limite deve estar entre 1 e 1000")
        return v 