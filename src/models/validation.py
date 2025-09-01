"""
Modelos de validação para tools FastMCP MongoDB.

Este módulo contém os schemas Pydantic para validação robusta
de entrada nas tools do servidor MCP MongoDB.
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field, field_validator
import re


class DatabaseName(BaseModel):
    """Validação para nomes de database MongoDB."""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Nome do database MongoDB (1-64 caracteres)"
    )
    
    @field_validator('name')
    def validate_database_name(cls, v):
        """Valida nome do database conforme especificações MongoDB."""
        if not v or not v.strip():
            raise ValueError("Nome do database não pode ser vazio")
        
        v = v.strip()
        
        # Caracteres proibidos no MongoDB
        invalid_chars = ['/', '\\', '.', ' ', '"', '$']
        for char in invalid_chars:
            if char in v:
                raise ValueError(f"Nome do database não pode conter '{char}'")
        
        # Nomes reservados
        reserved_names = ['admin', 'local', 'config']
        if v.lower() in reserved_names:
            raise ValueError(f"Nome '{v}' é reservado pelo sistema MongoDB")
        
        return v


class CollectionName(BaseModel):
    """Validação para nomes de collection MongoDB."""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Nome da collection MongoDB (1-120 caracteres)"
    )
    
    @field_validator('name')
    def validate_collection_name(cls, v):
        """Valida nome da collection conforme especificações MongoDB."""
        if not v or not v.strip():
            raise ValueError("Nome da collection não pode ser vazio")
        
        v = v.strip()
        
        # Não pode começar com 'system.'
        if v.startswith('system.'):
            raise ValueError("Nome da collection não pode começar com 'system.'")
        
        # Não pode conter '$' (exceto em posições específicas permitidas)
        if '$' in v and not v.startswith('oplog.$'):
            raise ValueError("Nome da collection não pode conter '$'")
        
        # Não pode estar vazio após o trim
        if not v:
            raise ValueError("Nome da collection não pode ser apenas espaços")
        
        return v


class ConnectionConfig(BaseModel):
    """Configuração de conexão MongoDB."""
    
    uri: str = Field(
        ...,
        min_length=10,
        description="URI de conexão MongoDB"
    )
    
    max_pool_size: int = Field(
        default=10,
        ge=1,
        le=1000,
        description="Tamanho máximo do pool de conexões (1-1000)"
    )
    
    @field_validator('uri')
    def validate_mongodb_uri(cls, v):
        """Valida URI do MongoDB."""
        if not v.startswith(('mongodb://', 'mongodb+srv://')):
            raise ValueError("URI deve começar com 'mongodb://' ou 'mongodb+srv://'")
        
        # Remove credenciais da validação por segurança
        if '@' in v:
            # Verifica formato básico sem expor credenciais
            parts = v.split('@')
            if len(parts) != 2:
                raise ValueError("Formato de URI inválido")
        
        return v


class DocumentQuery(BaseModel):
    """Query para buscar documentos."""
    
    database_name: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Nome do database"
    )
    
    collection_name: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Nome da collection"
    )
    
    field: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Campo para busca"
    )
    
    value: Union[str, int, float, bool] = Field(
        ...,
        description="Valor para busca"
    )
    
    limit: int = Field(
        default=20,
        ge=1,
        le=1000,
        description="Limite de resultados (1-1000)"
    )


class DocumentInsert(BaseModel):
    """Dados para inserir documento."""
    
    database_name: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Nome do database"
    )
    
    collection_name: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Nome da collection"
    )
    
    document: Dict[str, Any] = Field(
        ...,
        description="Documento a ser inserido"
    )
    
    @field_validator('document')
    def validate_document(cls, v):
        """Valida estrutura do documento."""
        if not isinstance(v, dict):
            raise ValueError("Documento deve ser um objeto JSON")
        
        if not v:
            raise ValueError("Documento não pode estar vazio")
        
        # Verifica tamanho aproximado (limite do MongoDB é 16MB)
        import json
        doc_size = len(json.dumps(v, default=str))
        if doc_size > 15 * 1024 * 1024:  # 15MB para margem de segurança
            raise ValueError("Documento muito grande (limite: ~15MB)")
        
        return v


class IndexSpec(BaseModel):
    """Especificação para criar índice."""
    
    database_name: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Nome do database"
    )
    
    collection_name: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Nome da collection"
    )
    
    index_spec: Dict[str, Union[int, str]] = Field(
        ...,
        description="Especificação do índice (campo: direção)"
    )
    
    index_options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Opções adicionais para o índice"
    )
    
    @field_validator('index_spec')
    def validate_index_spec(cls, v):
        """Valida especificação do índice."""
        if not v:
            raise ValueError("Especificação do índice não pode estar vazia")
        
        for field, direction in v.items():
            if not isinstance(field, str) or not field.strip():
                raise ValueError("Nome do campo deve ser uma string não vazia")
            
            # Direções válidas no MongoDB
            valid_directions = [1, -1, '2d', '2dsphere', 'text', 'hashed']
            if direction not in valid_directions:
                raise ValueError(f"Direção inválida '{direction}'. Use: {valid_directions}")
        
        return v


class PaginationParams(BaseModel):
    """Parâmetros de paginação."""
    
    skip: int = Field(
        default=0,
        ge=0,
        le=100000,
        description="Número de documentos para pular (0-100000)"
    )
    
    limit: int = Field(
        default=20,
        ge=1,
        le=1000,
        description="Limite de resultados por página (1-1000)"
    )
    
    @field_validator('skip')
    def validate_skip(cls, v):
        """Valida valor do skip."""
        if v > 50000:  # Aviso para performance
            import warnings
            warnings.warn("Valores altos de 'skip' podem impactar performance")
        return v


class AggregationPipeline(BaseModel):
    """Pipeline de agregação MongoDB."""
    
    database_name: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Nome do database"
    )
    
    collection_name: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Nome da collection"
    )
    
    pipeline: List[Dict[str, Any]] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Pipeline de agregação (1-100 estágios)"
    )
    
    @field_validator('pipeline')
    def validate_pipeline(cls, v):
        """Valida pipeline de agregação."""
        if not v:
            raise ValueError("Pipeline não pode estar vazio")
        
        # Verifica se cada estágio é um dict válido
        for i, stage in enumerate(v):
            if not isinstance(stage, dict):
                raise ValueError(f"Estágio {i} deve ser um objeto")
            
            if not stage:
                raise ValueError(f"Estágio {i} não pode estar vazio")
            
            # Verifica se tem pelo menos uma operação válida
            stage_ops = list(stage.keys())
            if not any(op.startswith('$') for op in stage_ops):
                raise ValueError(f"Estágio {i} deve conter pelo menos uma operação ($match, $group, etc.)")
        
        return v