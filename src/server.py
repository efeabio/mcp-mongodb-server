"""
Servidor FastMCP para MongoDB
"""

from typing import Dict, Any, Optional, List
import logging
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from src.utils.logger import get_logger

# Configuração do logging
logging.basicConfig(level=logging.INFO)

# Inicialização do conector MongoDB (será configurado dinamicamente)
mongo_connector = None

# Logger
logger = get_logger(__name__)

# Lifespan Management
@asynccontextmanager
async def lifespan(server: FastMCP):
    """
    Context manager para gerenciar o ciclo de vida do servidor MCP.
    
    Startup: Inicializa recursos necessários
    Shutdown: Limpa recursos adequadamente
    """
    # Startup
    try:
        # Recursos serão inicializados dinamicamente quando necessário
        yield
    except Exception as e:
        logger.error("Erro durante inicialização do servidor", error=str(e))
        raise
    finally:
        # Cleanup
        try:
            if mongo_connector:
                await mongo_connector.aclose()
        except Exception as e:
            logger.error("Erro durante finalização do servidor", error=str(e))

# Criação do servidor FastMCP com lifespan
server = FastMCP(
    name="mongodb-info-server",
    instructions="""
    Servidor MCP para interação com MongoDB que fornece acesso completo a:
    
    **Conexão**:
    - Configurar e testar conexões MongoDB
    - Verificar status de conectividade
    
    **Databases**:
    - Listar, criar e gerenciar databases
    - Obter estatísticas detalhadas de databases
    
    **Collections**:
    - Listar, criar, renomear e remover collections
    - Validar schemas e obter informações detalhadas
    
    **Documentos**:
    - Operações CRUD completas (Create, Read, Update, Delete)
    - Busca e listagem com filtros avançados
    - Suporte a aggregation pipelines
    
    **Índices**:
    - Criar, listar e remover índices
    - Análise de performance de queries
    
    **Estatísticas**:
    - Status do servidor MongoDB
    - Métricas de sistema e performance
    - Monitoramento de recursos
    
    Use as tools disponíveis para interagir com seu ambiente MongoDB de forma segura e eficiente.
    """,
    lifespan=lifespan,
    include_fastmcp_meta=True,
    on_duplicate_tools="warn",
    on_duplicate_resources="warn",
    on_duplicate_prompts="replace"
)

# Importação e inicialização das tools
def initialize_tools():
    """Inicializa todas as tools e suas dependências."""
    # Importa os módulos de tools para que os decorators sejam executados
    from src.tools import tools_documents, tools_collections, tools_indexes, tools_databases, tools_stats, tools_connection
    from src.tools.decorators import register_tools_with_server
    from src.tools.dependencies import DependencyContainer
    
    # Inicializa o DependencyContainer com o servidor
    DependencyContainer.initialize(mongo_connector, logger, server)
    
    # Inicializa as dependências de cada módulo (para compatibilidade)
    tools_connection.initialize_tools_connection(mongo_connector, logger, server)
    tools_documents.initialize_tools_documents(mongo_connector, logger, server)
    tools_collections.initialize_tools_collections(mongo_connector, logger, server)
    tools_indexes.initialize_tools_indexes(mongo_connector, logger, server)
    tools_databases.initialize_tools_databases(mongo_connector, logger, server)
    tools_stats.initialize_tools_stats(mongo_connector, logger, server)
    
    # Registra todas as tools automaticamente usando o sistema de decorators
    register_tools_with_server()
    
    # Registra tools que ainda não foram migradas para o sistema de decorators
    # Tools de documentos com validação robusta
    from src.models.validation import DocumentQuery, DocumentInsert
    from fastmcp.exceptions import ToolError
    from pydantic import ValidationError
    
    @server.tool()
    async def mongodb_list_documents(
        database_name: str,
        collection_name: str,
        limit: int = 20
    ) -> dict:
        """
        Lista documentos de uma collection MongoDB com validação robusta.
        
        Args:
            database_name: Nome do database MongoDB (1-64 caracteres, sem caracteres especiais)
            collection_name: Nome da collection (1-120 caracteres, não pode começar com 'system.')
            limit: Limite de documentos retornados (1-1000, padrão: 20)
            
        Returns:
            dict: Lista de documentos encontrados
            
        Raises:
            ToolError: Se os parâmetros forem inválidos ou ocorrer erro na operação
        """
        try:
            # Validação usando Pydantic
            query = DocumentQuery(
                database_name=database_name,
                collection_name=collection_name,
                field="_id",  # Campo dummy para validação
                value="dummy",  # Valor dummy para validação
                limit=limit
            )
            
            # Chama a função original com parâmetros validados
            return await tools_documents.list_documents(
                query.database_name,
                query.collection_name,
                query.limit
            )
            
        except ValidationError as e:
            # Converte erros de validação Pydantic em ToolError
            errors = "; ".join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors])
            raise ToolError(f"Parâmetros inválidos: {errors}")
        except Exception as e:
            raise ToolError(f"Erro ao listar documentos: {str(e)}")
    
    @server.tool()
    async def mongodb_get_document(
        database_name: str, 
        collection_name: str, 
        field: str, 
        value: str
    ) -> dict:
        """
        Busca um documento específico em uma collection MongoDB.
        
        Args:
            database_name: Nome do database MongoDB (1-64 caracteres)
            collection_name: Nome da collection (1-120 caracteres)
            field: Campo para busca (1-100 caracteres)
            value: Valor para buscar no campo especificado
            
        Returns:
            dict: Documento encontrado ou informações sobre a busca
            
        Raises:
            ToolError: Se os parâmetros forem inválidos ou ocorrer erro na operação
        """
        try:
            # Validação usando Pydantic
            query = DocumentQuery(
                database_name=database_name,
                collection_name=collection_name,
                field=field,
                value=value
            )
            
            return await tools_documents.get_document(
                query.database_name,
                query.collection_name,
                query.field,
                query.value
            )
            
        except ValidationError as e:
            errors = "; ".join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors])
            raise ToolError(f"Parâmetros inválidos: {errors}")
        except Exception as e:
            raise ToolError(f"Erro ao buscar documento: {str(e)}")
    
    @server.tool()
    async def mongodb_insert_document(
        database_name: str, 
        collection_name: str, 
        document: dict
    ) -> dict:
        """
        Insere um documento em uma collection MongoDB com validação robusta.
        
        Args:
            database_name: Nome do database MongoDB (1-64 caracteres)
            collection_name: Nome da collection (1-120 caracteres) 
            document: Documento JSON a ser inserido (máximo ~15MB)
            
        Returns:
            dict: Resultado da inserção incluindo ID gerado
            
        Raises:
            ToolError: Se os parâmetros forem inválidos ou ocorrer erro na operação
        """
        try:
            # Validação usando Pydantic
            insert_data = DocumentInsert(
                database_name=database_name,
                collection_name=collection_name,
                document=document
            )
            
            return await tools_documents.insert_document(
                insert_data.database_name,
                insert_data.collection_name,
                insert_data.document
            )
            
        except ValidationError as e:
            errors = "; ".join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors])
            raise ToolError(f"Parâmetros inválidos: {errors}")
        except Exception as e:
            raise ToolError(f"Erro ao inserir documento: {str(e)}")
    
    @server.tool()
    async def mongodb_update_document(database_name: str, collection_name: str, field: str, value: str, update: dict):
        return await tools_documents.update_document(database_name, collection_name, field, value, update)
    
    @server.tool()
    async def mongodb_delete_document(database_name: str, collection_name: str, field: str, value: str):
        return await tools_documents.delete_document(database_name, collection_name, field, value)
    
    # Tools de coleções
    @server.tool()
    async def mongodb_list_collections(database_name: str):
        return await tools_collections.list_collections(database_name)
    
    @server.tool()
    async def mongodb_create_collection(database_name: str, collection_name: str):
        return await tools_collections.create_collection(database_name, collection_name)
    
    @server.tool()
    async def mongodb_drop_collection(database_name: str, collection_name: str):
        return await tools_collections.drop_collection(database_name, collection_name)
    
    @server.tool()
    async def mongodb_get_collection_info(database_name: str, collection_name: str):
        return await tools_collections.get_collection_info(database_name, collection_name)
    
    # Tools de databases
    @server.tool()
    async def mongodb_list_databases():
        return await tools_databases.list_databases()
    
    @server.tool()
    async def mongodb_get_database_info(database_name: str):
        return await tools_databases.get_database_info(database_name)
    
    @server.tool()
    async def mongodb_create_database(database_name: str):
        return await tools_databases.create_database(database_name)
    
    @server.tool()
    async def mongodb_drop_database(database_name: str):
        return await tools_databases.drop_database(database_name)
    
    # Tools de indexes
    @server.tool()
    async def mongodb_list_indexes(database_name: str, collection_name: str):
        return await tools_indexes.list_indexes(database_name, collection_name)
    
    @server.tool()
    async def mongodb_create_index(database_name: str, collection_name: str, index_spec: dict, index_options: dict = None):
        return await tools_indexes.create_index(database_name, collection_name, index_spec, index_options)
    
    @server.tool()
    async def mongodb_drop_index(database_name: str, collection_name: str, index_name: str):
        return await tools_indexes.drop_index(database_name, collection_name, index_name)
    
    # Tools de estatísticas
    @server.tool()
    async def mongodb_get_server_status():
        return await tools_stats.get_server_status()
    
    @server.tool()
    async def mongodb_get_system_stats():
        return await tools_stats.get_system_stats()

# Funções de tools para compatibilidade com testes
async def list_databases():
    """Lista todos os databases."""
    try:
        from src.tools import tools_databases
        return await tools_databases.list_databases()
    except Exception as e:
        return {"status": "error", "error": f"Erro ao listar databases: {str(e)}"}

async def get_database_info(database_name: str):
    """Obtém informações de um database."""
    try:
        from src.tools import tools_databases
        return await tools_databases.get_database_info(database_name)
    except Exception as e:
        return {"status": "error", "error": f"Erro ao obter informações do database: {str(e)}"}

async def list_collections(database_name: str):
    """Lista collections de um database."""
    try:
        from src.tools import tools_collections
        return await tools_collections.list_collections(database_name)
    except Exception as e:
        return {"status": "error", "error": f"Erro ao listar collections: {str(e)}"}

async def get_collection_info(database_name: str, collection_name: str):
    """Obtém informações de uma collection."""
    try:
        from src.tools import tools_collections
        return await tools_collections.validate_collection(database_name, collection_name)
    except Exception as e:
        return {"status": "error", "error": f"Erro ao obter informações da collection: {str(e)}"}

async def get_server_status():
    """Obtém status do servidor."""
    try:
        from src.tools import tools_stats
        return await tools_stats.get_server_status()
    except Exception as e:
        return {"status": "error", "error": f"Erro ao obter status do servidor: {str(e)}"}

async def get_system_stats():
    """Obtém estatísticas do sistema."""
    try:
        from src.tools import tools_stats
        return await tools_stats.get_system_stats()
    except Exception as e:
        return {"status": "error", "error": f"Erro ao obter estatísticas do sistema: {str(e)}"}

# Inicializa as tools
initialize_tools()

# Cleanup é gerenciado pelo lifespan context manager 