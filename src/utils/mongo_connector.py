"""
Conector MongoDB para o FastMCP Server.

Este módulo contém o conector otimizado para MongoDB com connection pooling
e tratamento de erros robusto.
"""

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from typing import List, Dict, Any, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

from src.core.exceptions import (
    MongoDBConnectionError,
    DatabaseNotFoundError,
    CollectionNotFoundError,
    AuthenticationError,
    TimeoutError
)
from src.utils.logger import get_logger
from src.models.schemas import DatabaseInfo, CollectionInfo, ServerStatus


class MongoDBConnector:
    """
    Conector otimizado para MongoDB.
    
    Fornece métodos assíncronos para interagir com o MongoDB,
    incluindo connection pooling e tratamento de erros.
    """
    
    def __init__(self, uri: str, max_pool_size: int = 10):
        """
        Inicializa conector MongoDB.
        
        Args:
            uri: URI de conexão com MongoDB
            max_pool_size: Número máximo de conexões no pool
        """
        self.uri = uri
        self.max_pool_size = max_pool_size
        self.logger = get_logger(__name__)
        self._executor = ThreadPoolExecutor(max_workers=max_pool_size)
        
        try:
            self.client = MongoClient(
                uri,
                maxPoolSize=max_pool_size,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=30000,
                retryWrites=True,
                retryReads=True
            )
            # Testa conexão
            self.client.admin.command('ping')
            self.logger.info("Conectado ao MongoDB", uri=uri)
        except Exception as e:
            self.logger.error("Erro ao conectar ao MongoDB", uri=uri, error=str(e))
            raise MongoDBConnectionError(f"Erro ao conectar ao MongoDB: {str(e)}")
    
    async def list_databases(self) -> List[Dict[str, Any]]:
        """
        Lista todos os databases disponíveis.
        
        Returns:
            Lista de databases com informações básicas
            
        Raises:
            MongoDBConnectionError: Se não conseguir conectar ao MongoDB
        """
        try:
            loop = asyncio.get_event_loop()
            databases = await loop.run_in_executor(
                self._executor,
                self.client.list_database_names
            )
            
            result = []
            for db_name in databases:
                if db_name not in ['admin', 'local', 'config']:  # Filtra databases do sistema
                    db_info = await self.get_database_info(db_name)
                    result.append({
                        "name": db_info.name,
                        "size_on_disk": db_info.size_on_disk,
                        "collections": db_info.collections,
                        "objects": db_info.objects
                    })
            
            self.logger.info("Databases listados com sucesso", count=len(result))
            return result
            
        except Exception as e:
            self.logger.error("Erro ao listar databases", error=str(e))
            raise MongoDBConnectionError(f"Erro ao listar databases: {str(e)}")
    
    async def get_database_info(self, database_name: str) -> DatabaseInfo:
        """
        Retorna informações detalhadas de um database.
        
        Args:
            database_name: Nome do database
            
        Returns:
            DatabaseInfo: Informações detalhadas do database
            
        Raises:
            DatabaseNotFoundError: Se o database não existir
            MongoDBConnectionError: Se não conseguir conectar ao MongoDB
        """
        try:
            loop = asyncio.get_event_loop()
            
            # Verifica se o database existe
            db_names = await loop.run_in_executor(
                self._executor,
                self.client.list_database_names
            )
            
            if database_name not in db_names:
                raise DatabaseNotFoundError(f"Database '{database_name}' não encontrado")
            
            # Obtém informações do database
            db = self.client[database_name]
            stats = await loop.run_in_executor(
                self._executor,
                db.command,
                "dbStats"
            )
            
            # Obtém lista de collections
            collections = await loop.run_in_executor(
                self._executor,
                db.list_collection_names
            )
            
            db_info = DatabaseInfo(
                name=database_name,
                size_on_disk=stats.get('dataSize', 0),
                collections=len(collections),
                objects=stats.get('objects', 0),
                avg_obj_size=stats.get('avgObjSize', 0),
                data_size=stats.get('dataSize', 0),
                storage_size=stats.get('storageSize', 0),
                indexes=stats.get('indexes', 0),
                index_size=stats.get('indexSize', 0)
            )
            
            self.logger.info("Informações do database obtidas", 
                           database=database_name)
            return db_info
            
        except DatabaseNotFoundError:
            raise
        except Exception as e:
            self.logger.error("Erro ao obter informações do database", 
                            database=database_name, error=str(e))
            raise MongoDBConnectionError(f"Erro ao obter informações do database: {str(e)}")
    
    async def list_collections(self, database_name: str) -> List[Dict[str, Any]]:
        """
        Lista todas as collections de um database.
        
        Args:
            database_name: Nome do database
            
        Returns:
            Lista de collections com informações básicas
            
        Raises:
            DatabaseNotFoundError: Se o database não existir
            MongoDBConnectionError: Se não conseguir conectar ao MongoDB
        """
        try:
            loop = asyncio.get_event_loop()
            
            # Verifica se o database existe
            db_names = await loop.run_in_executor(
                self._executor,
                self.client.list_database_names
            )
            
            if database_name not in db_names:
                raise DatabaseNotFoundError(f"Database '{database_name}' não encontrado")
            
            db = self.client[database_name]
            collections = await loop.run_in_executor(
                self._executor,
                db.list_collection_names
            )
            
            result = []
            for collection_name in collections:
                collection_info = await self.get_collection_info(database_name, collection_name)
                result.append({
                    "name": collection_info.name,
                    "count": collection_info.count,
                    "size": collection_info.size,
                    "storage_size": collection_info.storage_size,
                    "total_index_size": collection_info.total_index_size
                })
            
            self.logger.info("Collections listadas com sucesso", 
                           database=database_name, count=len(result))
            return result
            
        except DatabaseNotFoundError:
            raise
        except Exception as e:
            self.logger.error("Erro ao listar collections", 
                            database=database_name, error=str(e))
            raise MongoDBConnectionError(f"Erro ao listar collections: {str(e)}")
    
    async def get_collection_info(self, database_name: str, collection_name: str) -> CollectionInfo:
        """
        Retorna informações detalhadas de uma collection.
        
        Args:
            database_name: Nome do database
            collection_name: Nome da collection
            
        Returns:
            CollectionInfo: Informações detalhadas da collection
            
        Raises:
            DatabaseNotFoundError: Se o database não existir
            CollectionNotFoundError: Se a collection não existir
            MongoDBConnectionError: Se não conseguir conectar ao MongoDB
        """
        try:
            loop = asyncio.get_event_loop()
            
            # Verifica se o database existe
            db_names = await loop.run_in_executor(
                self._executor,
                self.client.list_database_names
            )
            
            if database_name not in db_names:
                raise DatabaseNotFoundError(f"Database '{database_name}' não encontrado")
            
            db = self.client[database_name]
            
            # Verifica se a collection existe
            collections = await loop.run_in_executor(
                self._executor,
                db.list_collection_names
            )
            
            if collection_name not in collections:
                raise CollectionNotFoundError(f"Collection '{collection_name}' não encontrada")
            
            collection = db[collection_name]
            
            # Obtém estatísticas da collection
            stats = await loop.run_in_executor(
                self._executor,
                collection.aggregate,
                [{"$collStats": {"storage": {}, "count": {}, "latencyStats": {}}}]
            )
            
            stats_list = list(stats)
            if not stats_list:
                raise CollectionNotFoundError(f"Collection '{collection_name}' não encontrada")
            
            stats_data = stats_list[0]
            
            # Obtém índices
            indexes = await loop.run_in_executor(
                self._executor,
                collection.list_indexes
            )
            
            indexes_list = list(indexes)
            
            collection_info = CollectionInfo(
                name=collection_name,
                count=stats_data.get('count', 0),
                size=stats_data.get('size', 0),
                avg_obj_size=stats_data.get('avgObjSize', 0),
                storage_size=stats_data.get('storageSize', 0),
                total_index_size=stats_data.get('totalIndexSize', 0),
                indexes=[{"name": idx.get('name'), "key": idx.get('key')} for idx in indexes_list]
            )
            
            self.logger.info("Informações da collection obtidas", 
                           database=database_name, collection=collection_name)
            return collection_info
            
        except (DatabaseNotFoundError, CollectionNotFoundError):
            raise
        except Exception as e:
            self.logger.error("Erro ao obter informações da collection", 
                            database=database_name, collection=collection_name, error=str(e))
            raise MongoDBConnectionError(f"Erro ao obter informações da collection: {str(e)}")
    
    async def get_server_status(self) -> ServerStatus:
        """
        Retorna status geral do servidor MongoDB.
        
        Returns:
            ServerStatus: Status detalhado do servidor
            
        Raises:
            MongoDBConnectionError: Se não conseguir conectar ao MongoDB
        """
        try:
            loop = asyncio.get_event_loop()
            
            # Obtém status do servidor
            status = await loop.run_in_executor(
                self._executor,
                self.client.admin.command,
                "serverStatus"
            )
            
            server_status = ServerStatus(
                version=status.get('version', ''),
                uptime=status.get('uptime', 0),
                connections=status.get('connections', {}),
                memory=status.get('mem', {}),
                operations=status.get('opcounters', {}),
                network=status.get('network', {})
            )
            
            self.logger.info("Status do servidor obtido com sucesso")
            return server_status
            
        except Exception as e:
            self.logger.error("Erro ao obter status do servidor", error=str(e))
            raise MongoDBConnectionError(f"Erro ao obter status do servidor: {str(e)}")
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do sistema.
        
        Returns:
            Dicionário com estatísticas do sistema
            
        Raises:
            MongoDBConnectionError: Se não conseguir conectar ao MongoDB
        """
        try:
            loop = asyncio.get_event_loop()
            
            # Obtém estatísticas do sistema
            stats = await loop.run_in_executor(
                self._executor,
                self.client.admin.command,
                "dbStats"
            )
            
            # Obtém informações de databases
            databases = await self.list_databases()
            
            system_stats = {
                "databases_count": len(databases),
                "total_collections": sum(db.get('collections', 0) for db in databases),
                "total_objects": sum(db.get('objects', 0) for db in databases),
                "total_size": sum(db.get('size_on_disk', 0) for db in databases),
                "admin_stats": stats
            }
            
            self.logger.info("Estatísticas do sistema obtidas com sucesso")
            return system_stats
            
        except Exception as e:
            self.logger.error("Erro ao obter estatísticas do sistema", error=str(e))
            raise MongoDBConnectionError(f"Erro ao obter estatísticas do sistema: {str(e)}")
    
    def close(self) -> None:
        """
        Fecha conexões com o MongoDB.
        """
        try:
            self.client.close()
            self._executor.shutdown(wait=True)
            self.logger.info("Conexões com MongoDB fechadas")
        except Exception as e:
            self.logger.error("Erro ao fechar conexões", error=str(e))
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 