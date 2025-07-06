"""
Serviço de Collection para o FastMCP MongoDB Server.

Este módulo contém os serviços relacionados a collections MongoDB,
incluindo listagem e obtenção de informações detalhadas.
"""

from typing import List, Dict, Any
from src.utils.mongo_connector import MongoDBConnector
from src.models.schemas import CollectionInfo, CollectionQuery
from src.core.exceptions import DatabaseNotFoundError, CollectionNotFoundError, MongoDBConnectionError
from src.utils.logger import get_logger


class CollectionService:
    """
    Serviço para operações relacionadas a collections MongoDB.
    
    Fornece métodos para listar collections e obter informações detalhadas,
    incluindo validação de entrada e tratamento de erros.
    """
    
    def __init__(self, mongo_connector: MongoDBConnector):
        """
        Inicializa o serviço de collection.
        
        Args:
            mongo_connector: Instância do conector MongoDB
        """
        self.mongo_connector = mongo_connector
        self.logger = get_logger(__name__)
    
    async def list_collections(self, database_name: str) -> List[Dict[str, Any]]:
        """
        Lista todas as collections de um database MongoDB.
        
        Args:
            database_name: Nome do database
            
        Returns:
            Lista de collections com informações básicas
            
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
            
            self.logger.info("Listando collections do database", database=database_name)
            
            collections = await self.mongo_connector.list_collections(database_name)
            
            self.logger.info("Collections listadas com sucesso", 
                           database=database_name, count=len(collections))
            return collections
            
        except ValueError:
            raise
        except DatabaseNotFoundError:
            raise
        except Exception as e:
            self.logger.error("Erro no serviço ao listar collections", 
                            database=database_name, error=str(e))
            raise
    
    async def get_collection_info(self, database_name: str, collection_name: str) -> CollectionInfo:
        """
        Retorna informações detalhadas de uma collection MongoDB.
        
        Args:
            database_name: Nome do database
            collection_name: Nome da collection
            
        Returns:
            CollectionInfo: Informações detalhadas da collection
            
        Raises:
            ValueError: Se database_name ou collection_name forem vazios ou inválidos
            DatabaseNotFoundError: Se o database não existir
            CollectionNotFoundError: Se a collection não existir
            MongoDBConnectionError: Se não conseguir conectar ao MongoDB
        """
        try:
            # Valida entrada
            if not database_name or not database_name.strip():
                raise ValueError("Nome do database não pode ser vazio")
            
            if not collection_name or not collection_name.strip():
                raise ValueError("Nome da collection não pode ser vazio")
            
            database_name = database_name.strip()
            collection_name = collection_name.strip()
            
            # Valida tamanho dos nomes
            if len(database_name) > 64:
                raise ValueError("Nome do database deve ter no máximo 64 caracteres")
            
            if len(collection_name) > 255:
                raise ValueError("Nome da collection deve ter no máximo 255 caracteres")
            
            self.logger.info("Obtendo informações da collection", 
                           database=database_name, collection=collection_name)
            
            collection_info = await self.mongo_connector.get_collection_info(
                database_name, collection_name
            )
            
            self.logger.info("Informações da collection obtidas com sucesso", 
                           database=database_name, collection=collection_name)
            return collection_info
            
        except ValueError:
            raise
        except DatabaseNotFoundError:
            raise
        except CollectionNotFoundError:
            raise
        except Exception as e:
            self.logger.error("Erro no serviço ao obter informações da collection", 
                            database=database_name, collection=collection_name, error=str(e))
            raise
    
    async def validate_collection_query(self, query: CollectionQuery) -> CollectionQuery:
        """
        Valida uma query de collection.
        
        Args:
            query: Query a ser validada
            
        Returns:
            CollectionQuery: Query validada
            
        Raises:
            ValueError: Se a query for inválida
        """
        try:
            # Validações adicionais podem ser adicionadas aqui
            if not query.database_name or not query.database_name.strip():
                raise ValueError("Nome do database não pode ser vazio")
            
            if not query.collection_name or not query.collection_name.strip():
                raise ValueError("Nome da collection não pode ser vazio")
            
            if query.limit <= 0 or query.limit > 1000:
                raise ValueError("Limite deve estar entre 1 e 1000")
            
            self.logger.debug("Query de collection validada", 
                            database=query.database_name, 
                            collection=query.collection_name, 
                            limit=query.limit)
            return query
            
        except Exception as e:
            self.logger.error("Erro ao validar query de collection", error=str(e))
            raise ValueError(f"Query de collection inválida: {str(e)}")
    
    async def get_collection_summary(self, database_name: str) -> Dict[str, Any]:
        """
        Retorna um resumo das collections de um database.
        
        Args:
            database_name: Nome do database
            
        Returns:
            Dicionário com resumo das collections
            
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
            
            self.logger.info("Gerando resumo das collections", database=database_name)
            
            collections = await self.list_collections(database_name)
            
            total_collections = len(collections)
            total_documents = sum(col.get('count', 0) for col in collections)
            total_size = sum(col.get('size', 0) for col in collections)
            total_storage_size = sum(col.get('storage_size', 0) for col in collections)
            total_index_size = sum(col.get('total_index_size', 0) for col in collections)
            
            summary = {
                "database_name": database_name,
                "total_collections": total_collections,
                "total_documents": total_documents,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "total_storage_size_bytes": total_storage_size,
                "total_storage_size_mb": round(total_storage_size / (1024 * 1024), 2),
                "total_index_size_bytes": total_index_size,
                "total_index_size_mb": round(total_index_size / (1024 * 1024), 2),
                "collections": collections
            }
            
            self.logger.info("Resumo das collections gerado com sucesso", 
                           database=database_name, total_collections=total_collections)
            return summary
            
        except ValueError:
            raise
        except DatabaseNotFoundError:
            raise
        except Exception as e:
            self.logger.error("Erro ao gerar resumo das collections", 
                            database=database_name, error=str(e))
            raise
    
    async def get_collection_stats(self, database_name: str, collection_name: str) -> Dict[str, Any]:
        """
        Retorna estatísticas detalhadas de uma collection.
        
        Args:
            database_name: Nome do database
            collection_name: Nome da collection
            
        Returns:
            Dicionário com estatísticas da collection
            
        Raises:
            ValueError: Se database_name ou collection_name forem vazios ou inválidos
            DatabaseNotFoundError: Se o database não existir
            CollectionNotFoundError: Se a collection não existir
            MongoDBConnectionError: Se não conseguir conectar ao MongoDB
        """
        try:
            # Obtém informações básicas da collection
            collection_info = await self.get_collection_info(database_name, collection_name)
            
            # Calcula estatísticas adicionais
            stats = {
                "name": collection_info.name,
                "count": collection_info.count,
                "size_bytes": collection_info.size,
                "size_mb": round(collection_info.size / (1024 * 1024), 2),
                "avg_obj_size_bytes": collection_info.avg_obj_size,
                "avg_obj_size_kb": round(collection_info.avg_obj_size / 1024, 2) if collection_info.avg_obj_size else 0,
                "storage_size_bytes": collection_info.storage_size,
                "storage_size_mb": round(collection_info.storage_size / (1024 * 1024), 2),
                "total_index_size_bytes": collection_info.total_index_size,
                "total_index_size_mb": round(collection_info.total_index_size / (1024 * 1024), 2),
                "indexes_count": len(collection_info.indexes),
                "indexes": collection_info.indexes
            }
            
            self.logger.info("Estatísticas da collection obtidas com sucesso", 
                           database=database_name, collection=collection_name)
            return stats
            
        except ValueError:
            raise
        except DatabaseNotFoundError:
            raise
        except CollectionNotFoundError:
            raise
        except Exception as e:
            self.logger.error("Erro ao obter estatísticas da collection", 
                            database=database_name, collection=collection_name, error=str(e))
            raise 