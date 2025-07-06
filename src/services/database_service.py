"""
Serviço de Database para o FastMCP MongoDB Server.

Este módulo contém os serviços relacionados a databases MongoDB,
incluindo listagem e obtenção de informações detalhadas.
"""

from typing import List, Dict, Any
from src.utils.mongo_connector import MongoDBConnector
from src.models.schemas import DatabaseInfo, DatabaseQuery
from src.core.exceptions import DatabaseNotFoundError, MongoDBConnectionError
from src.utils.logger import get_logger


class DatabaseService:
    """
    Serviço para operações relacionadas a databases MongoDB.
    
    Fornece métodos para listar databases e obter informações detalhadas,
    incluindo validação de entrada e tratamento de erros.
    """
    
    def __init__(self, mongo_connector: MongoDBConnector):
        """
        Inicializa o serviço de database.
        
        Args:
            mongo_connector: Instância do conector MongoDB
        """
        self.mongo_connector = mongo_connector
        self.logger = get_logger(__name__)
    
    async def list_databases(self) -> List[Dict[str, Any]]:
        """
        Lista todos os databases disponíveis no MongoDB.
        
        Returns:
            Lista de databases com informações básicas
            
        Raises:
            MongoDBConnectionError: Se não conseguir conectar ao MongoDB
        """
        try:
            self.logger.info("Iniciando listagem de databases")
            databases = await self.mongo_connector.list_databases()
            
            self.logger.info("Databases listados com sucesso", count=len(databases))
            return databases
            
        except Exception as e:
            self.logger.error("Erro no serviço ao listar databases", error=str(e))
            raise
    
    async def get_database_info(self, database_name: str) -> DatabaseInfo:
        """
        Retorna informações detalhadas de um database MongoDB.
        
        Args:
            database_name: Nome do database
            
        Returns:
            DatabaseInfo: Informações detalhadas do database
            
        Raises:
            ValueError: Se database_name for vazio ou inválido
            DatabaseNotFoundError: Se o database não existir
            MongoDBConnectionError: Se não conseguir conectar ao MongoDB
        """
        try:
            # Valida entrada
            if not database_name or not database_name.strip():
                raise ValueError("Nome do database não pode ser vazio")
            
            database_name = database_name.strip()
            
            # Valida tamanho do nome
            if len(database_name) > 64:
                raise ValueError("Nome do database deve ter no máximo 64 caracteres")
            
            self.logger.info("Obtendo informações do database", database=database_name)
            
            # Obtém informações do database
            db_info = await self.mongo_connector.get_database_info(database_name)
            
            self.logger.info("Informações do database obtidas com sucesso", 
                           database=database_name)
            return db_info
            
        except ValueError:
            raise
        except DatabaseNotFoundError:
            raise
        except Exception as e:
            self.logger.error("Erro no serviço ao obter informações do database", 
                            database=database_name, error=str(e))
            raise
    
    async def validate_database_query(self, query: DatabaseQuery) -> DatabaseQuery:
        """
        Valida uma query de database.
        
        Args:
            query: Query a ser validada
            
        Returns:
            DatabaseQuery: Query validada
            
        Raises:
            ValueError: Se a query for inválida
        """
        try:
            # Validações adicionais podem ser adicionadas aqui
            if not query.database_name or not query.database_name.strip():
                raise ValueError("Nome do database não pode ser vazio")
            
            if query.limit <= 0 or query.limit > 1000:
                raise ValueError("Limite deve estar entre 1 e 1000")
            
            self.logger.debug("Query de database validada", 
                            database=query.database_name, limit=query.limit)
            return query
            
        except Exception as e:
            self.logger.error("Erro ao validar query de database", error=str(e))
            raise ValueError(f"Query de database inválida: {str(e)}")
    
    async def get_database_summary(self) -> Dict[str, Any]:
        """
        Retorna um resumo de todos os databases.
        
        Returns:
            Dicionário com resumo dos databases
            
        Raises:
            MongoDBConnectionError: Se não conseguir conectar ao MongoDB
        """
        try:
            self.logger.info("Gerando resumo dos databases")
            
            databases = await self.list_databases()
            
            total_databases = len(databases)
            total_collections = sum(db.get('collections', 0) for db in databases)
            total_objects = sum(db.get('objects', 0) for db in databases)
            total_size = sum(db.get('size_on_disk', 0) for db in databases)
            
            summary = {
                "total_databases": total_databases,
                "total_collections": total_collections,
                "total_objects": total_objects,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "databases": databases
            }
            
            self.logger.info("Resumo dos databases gerado com sucesso", 
                           total_databases=total_databases)
            return summary
            
        except Exception as e:
            self.logger.error("Erro ao gerar resumo dos databases", error=str(e))
            raise 