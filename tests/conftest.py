"""
Configuração de testes para o FastMCP MongoDB Server.

Este módulo contém fixtures e configurações para os testes unitários.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from src.utils.mongo_connector import MongoDBConnector
from src.services.database_service import DatabaseService
from src.services.collection_service import CollectionService
from src.services.stats_service import StatsService
from src.models.schemas import DatabaseInfo, CollectionInfo, ServerStatus
from src.utils.logger import configure_logging_for_tests


@pytest.fixture(scope="session", autouse=True)
def setup_test_logging():
    """
    Configura logging para testes.
    """
    configure_logging_for_tests()


@pytest.fixture
def mock_mongo_client():
    """
    Mock do cliente MongoDB.
    """
    mock_client = MagicMock()
    
    # Mock para list_database_names
    mock_client.list_database_names.return_value = ["test_db", "admin", "local"]
    
    # Mock para admin.command
    mock_admin = MagicMock()
    mock_admin.command.return_value = {
        "version": "7.0.0",
        "uptime": 86400,
        "connections": {"current": 10, "available": 90},
        "mem": {"resident": 1073741824, "virtual": 2147483648},
        "opcounters": {"insert": 1000, "query": 5000, "update": 500, "delete": 100},
        "network": {"bytesIn": 1048576, "bytesOut": 2097152, "numRequests": 10000}
    }
    mock_client.admin = mock_admin
    
    # Mock para database
    mock_db = MagicMock()
    mock_db.command.return_value = {
        "collections": 5,
        "objects": 1000,
        "avgObjSize": 1024,
        "dataSize": 1048576,
        "storageSize": 2097152,
        "indexes": 3,
        "indexSize": 524288
    }
    mock_db.list_collection_names.return_value = ["users", "products"]
    mock_client.__getitem__.return_value = mock_db
    
    return mock_client


@pytest.fixture
def mock_mongo_connector(mock_mongo_client):
    """
    Mock do conector MongoDB.
    """
    connector = MagicMock(spec=MongoDBConnector)
    connector.client = mock_mongo_client
    
    # Mock para métodos assíncronos
    connector.list_databases = AsyncMock(return_value=[
        {
            "name": "test_db",
            "size_on_disk": 1048576,
            "collections": 5,
            "objects": 1000
        }
    ])
    
    connector.get_database_info = AsyncMock(return_value=DatabaseInfo(
        name="test_db",
        size_on_disk=1048576,
        collections=5,
        objects=1000,
        avg_obj_size=1024,
        data_size=1048576,
        storage_size=2097152,
        indexes=3,
        index_size=524288
    ))
    
    connector.list_collections = AsyncMock(return_value=[
        {
            "name": "users",
            "count": 500,
            "size": 524288,
            "storage_size": 1048576,
            "total_index_size": 262144
        }
    ])
    
    connector.get_collection_info = AsyncMock(return_value=CollectionInfo(
        name="users",
        count=500,
        size=524288,
        avg_obj_size=1024,
        storage_size=1048576,
        total_index_size=262144,
        indexes=[{"name": "_id_", "key": [["_id", 1]]}]
    ))
    
    connector.get_server_status = AsyncMock(return_value=ServerStatus(
        version="7.0.0",
        uptime=86400,
        connections={"current": 10, "available": 90},
        memory={"resident": 1073741824, "virtual": 2147483648},
        operations={"insert": 1000, "query": 5000, "update": 500, "delete": 100},
        network={"bytesIn": 1048576, "bytesOut": 2097152, "numRequests": 10000}
    ))
    
    connector.get_system_stats = AsyncMock(return_value={
        "databases_count": 5,
        "total_collections": 25,
        "total_objects": 10000,
        "total_size": 52428800,
        "admin_stats": {"collections": 0, "objects": 0, "dataSize": 0}
    })
    
    return connector


@pytest.fixture
def database_service(mock_mongo_connector):
    """
    Instância do serviço de database com mock.
    """
    return DatabaseService(mock_mongo_connector)


@pytest.fixture
def collection_service(mock_mongo_connector):
    """
    Instância do serviço de collection com mock.
    """
    return CollectionService(mock_mongo_connector)


@pytest.fixture
def stats_service(mock_mongo_connector):
    """
    Instância do serviço de estatísticas com mock.
    """
    return StatsService(mock_mongo_connector)


@pytest.fixture
def sample_database_info():
    """
    Dados de exemplo para DatabaseInfo.
    """
    return {
        "name": "test_db",
        "size_on_disk": 1048576,
        "collections": 5,
        "objects": 1000,
        "avg_obj_size": 1024,
        "data_size": 1048576,
        "storage_size": 2097152,
        "indexes": 3,
        "index_size": 524288
    }


@pytest.fixture
def sample_collection_info():
    """
    Dados de exemplo para CollectionInfo.
    """
    return {
        "name": "users",
        "count": 500,
        "size": 524288,
        "avg_obj_size": 1024,
        "storage_size": 1048576,
        "total_index_size": 262144,
        "indexes": [{"name": "_id_", "key": [["_id", 1]]}]
    }


@pytest.fixture
def sample_server_status():
    """
    Dados de exemplo para ServerStatus.
    """
    return {
        "version": "7.0.0",
        "uptime": 86400,
        "connections": {"current": 10, "available": 90},
        "memory": {"resident": 1073741824, "virtual": 2147483648},
        "operations": {"insert": 1000, "query": 5000, "update": 500, "delete": 100},
        "network": {"bytesIn": 1048576, "bytesOut": 2097152, "numRequests": 10000}
    } 