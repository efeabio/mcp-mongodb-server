"""
Testes unitários para os serviços do FastMCP MongoDB Server.

Este módulo testa os serviços de database, collection e estatísticas
usando mocks para simular o MongoDB.
"""

import pytest
from unittest.mock import AsyncMock
from src.services.database_service import DatabaseService
from src.services.collection_service import CollectionService
from src.services.stats_service import StatsService
from src.core.exceptions import DatabaseNotFoundError, CollectionNotFoundError
from src.models.schemas import DatabaseQuery, CollectionQuery
from pydantic import ValidationError


class TestDatabaseService:
    """Testes para o DatabaseService."""
    
    @pytest.mark.asyncio
    async def test_list_databases_success(self, database_service):
        """Testa listagem de databases com sucesso."""
        result = await database_service.list_databases()
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["name"] == "test_db"
        assert result[0]["collections"] == 5
        assert result[0]["objects"] == 1000
    
    @pytest.mark.asyncio
    async def test_get_database_info_success(self, database_service):
        """Testa obtenção de informações de database com sucesso."""
        result = await database_service.get_database_info("test_db")
        
        assert result.name == "test_db"
        assert result.size_on_disk == 1048576
        assert result.collections == 5
        assert result.objects == 1000
        assert result.avg_obj_size == 1024
    
    @pytest.mark.asyncio
    async def test_get_database_info_empty_name(self, database_service):
        """Testa erro com nome de database vazio."""
        with pytest.raises(ValueError, match="Nome do database não pode ser vazio"):
            await database_service.get_database_info("")
    
    @pytest.mark.asyncio
    async def test_get_database_info_whitespace_name(self, database_service):
        """Testa erro com nome de database apenas espaços."""
        with pytest.raises(ValueError, match="Nome do database não pode ser vazio"):
            await database_service.get_database_info("   ")
    
    @pytest.mark.asyncio
    async def test_get_database_info_long_name(self, database_service):
        """Testa erro com nome de database muito longo."""
        long_name = "a" * 65
        with pytest.raises(ValueError, match="Nome do database deve ter no máximo 64 caracteres"):
            await database_service.get_database_info(long_name)
    
    @pytest.mark.asyncio
    async def test_get_database_info_not_found(self, database_service, mock_mongo_connector):
        """Testa erro quando database não é encontrado."""
        mock_mongo_connector.get_database_info.side_effect = DatabaseNotFoundError("Database não encontrado")
        
        with pytest.raises(DatabaseNotFoundError):
            await database_service.get_database_info("nonexistent_db")
    
    @pytest.mark.asyncio
    async def test_validate_database_query_success(self, database_service):
        """Testa validação de query de database com sucesso."""
        query = DatabaseQuery(database_name="test_db", limit=100)
        result = await database_service.validate_database_query(query)
        
        assert result.database_name == "test_db"
        assert result.limit == 100
    
    @pytest.mark.asyncio
    async def test_validate_database_query_empty_name(self, database_service):
        """Testa erro de validação com nome vazio."""
        with pytest.raises(ValidationError):
            DatabaseQuery(database_name="", limit=100)
    
    @pytest.mark.asyncio
    async def test_validate_database_query_invalid_limit(self, database_service):
        """Testa erro de validação com limite inválido."""
        with pytest.raises(ValidationError):
            DatabaseQuery(database_name="test_db", limit=0)
    
    @pytest.mark.asyncio
    async def test_get_database_summary_success(self, database_service):
        """Testa obtenção de resumo de databases com sucesso."""
        result = await database_service.get_database_summary()
        
        assert result["total_databases"] == 1
        assert result["total_collections"] == 5
        assert result["total_objects"] == 1000
        assert result["total_size_bytes"] == 1048576
        assert result["total_size_mb"] == 1.0


class TestCollectionService:
    """Testes para o CollectionService."""
    
    @pytest.mark.asyncio
    async def test_list_collections_success(self, collection_service):
        """Testa listagem de collections com sucesso."""
        result = await collection_service.list_collections("test_db")
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["name"] == "users"
        assert result[0]["count"] == 500
        assert result[0]["size"] == 524288
    
    @pytest.mark.asyncio
    async def test_list_collections_empty_database_name(self, collection_service):
        """Testa erro com nome de database vazio."""
        with pytest.raises(ValueError, match="Nome do database não pode ser vazio"):
            await collection_service.list_collections("")
    
    @pytest.mark.asyncio
    async def test_list_collections_long_database_name(self, collection_service):
        """Testa erro com nome de database muito longo."""
        long_name = "a" * 65
        with pytest.raises(ValueError, match="Nome do database deve ter no máximo 64 caracteres"):
            await collection_service.list_collections(long_name)
    
    @pytest.mark.asyncio
    async def test_list_collections_database_not_found(self, collection_service, mock_mongo_connector):
        """Testa erro quando database não é encontrado."""
        mock_mongo_connector.list_collections.side_effect = DatabaseNotFoundError("Database não encontrado")
        
        with pytest.raises(DatabaseNotFoundError):
            await collection_service.list_collections("nonexistent_db")
    
    @pytest.mark.asyncio
    async def test_get_collection_info_success(self, collection_service):
        """Testa obtenção de informações de collection com sucesso."""
        result = await collection_service.get_collection_info("test_db", "users")
        
        assert result.name == "users"
        assert result.count == 500
        assert result.size == 524288
        assert result.avg_obj_size == 1024
        assert len(result.indexes) == 1
    
    @pytest.mark.asyncio
    async def test_get_collection_info_empty_database_name(self, collection_service):
        """Testa erro com nome de database vazio."""
        with pytest.raises(ValueError, match="Nome do database não pode ser vazio"):
            await collection_service.get_collection_info("", "users")
    
    @pytest.mark.asyncio
    async def test_get_collection_info_empty_collection_name(self, collection_service):
        """Testa erro com nome de collection vazio."""
        with pytest.raises(ValueError, match="Nome da collection não pode ser vazio"):
            await collection_service.get_collection_info("test_db", "")
    
    @pytest.mark.asyncio
    async def test_get_collection_info_long_collection_name(self, collection_service):
        """Testa erro com nome de collection muito longo."""
        long_name = "a" * 256
        with pytest.raises(ValueError, match="Nome da collection deve ter no máximo 255 caracteres"):
            await collection_service.get_collection_info("test_db", long_name)
    
    @pytest.mark.asyncio
    async def test_get_collection_info_collection_not_found(self, collection_service, mock_mongo_connector):
        """Testa erro quando collection não é encontrada."""
        mock_mongo_connector.get_collection_info.side_effect = CollectionNotFoundError("Collection não encontrada")
        
        with pytest.raises(CollectionNotFoundError):
            await collection_service.get_collection_info("test_db", "nonexistent_collection")
    
    @pytest.mark.asyncio
    async def test_validate_collection_query_success(self, collection_service):
        """Testa validação de query de collection com sucesso."""
        query = CollectionQuery(database_name="test_db", collection_name="users", limit=100)
        result = await collection_service.validate_collection_query(query)
        
        assert result.database_name == "test_db"
        assert result.collection_name == "users"
        assert result.limit == 100
    
    @pytest.mark.asyncio
    async def test_validate_collection_query_empty_database_name(self, collection_service):
        """Testa erro de validação com nome de database vazio."""
        with pytest.raises(ValidationError):
            CollectionQuery(database_name="", collection_name="users", limit=100)
    
    @pytest.mark.asyncio
    async def test_validate_collection_query_empty_collection_name(self, collection_service):
        """Testa erro de validação com nome de collection vazio."""
        with pytest.raises(ValidationError):
            CollectionQuery(database_name="test_db", collection_name="", limit=100)
    
    @pytest.mark.asyncio
    async def test_get_collection_summary_success(self, collection_service):
        """Testa obtenção de resumo de collections com sucesso."""
        result = await collection_service.get_collection_summary("test_db")
        
        assert result["database_name"] == "test_db"
        assert result["total_collections"] == 1
        assert result["total_documents"] == 500
        assert result["total_size_bytes"] == 524288
        assert result["total_size_mb"] == 0.5
    
    @pytest.mark.asyncio
    async def test_get_collection_stats_success(self, collection_service):
        """Testa obtenção de estatísticas de collection com sucesso."""
        result = await collection_service.get_collection_stats("test_db", "users")
        
        assert result["name"] == "users"
        assert result["count"] == 500
        assert result["size_bytes"] == 524288
        assert result["size_mb"] == 0.5
        assert result["indexes_count"] == 1


class TestStatsService:
    """Testes para o StatsService."""
    
    @pytest.mark.asyncio
    async def test_get_server_status_success(self, stats_service):
        """Testa obtenção de status do servidor com sucesso."""
        result = await stats_service.get_server_status()
        
        assert result.version == "7.0.0"
        assert result.uptime == 86400
        assert result.connections["current"] == 10
        assert result.connections["available"] == 90
        assert result.memory["resident"] == 1073741824
    
    @pytest.mark.asyncio
    async def test_get_system_stats_success(self, stats_service):
        """Testa obtenção de estatísticas do sistema com sucesso."""
        result = await stats_service.get_system_stats()
        
        assert result["databases_count"] == 5
        assert result["total_collections"] == 25
        assert result["total_objects"] == 10000
        assert result["total_size"] == 52428800
    
    @pytest.mark.asyncio
    async def test_get_server_health_success(self, stats_service):
        """Testa obtenção de informações de saúde do servidor com sucesso."""
        result = await stats_service.get_server_health()
        
        assert result["status"] == "healthy"
        assert result["version"] == "7.0.0"
        assert result["uptime_hours"] == 24.0
        assert result["uptime_days"] == 1.0
        assert result["connections"]["current"] == 10
        assert result["connections"]["available"] == 90
        assert result["memory"]["resident_mb"] == 1024.0
        assert result["memory"]["resident_gb"] == 1.0
    
    @pytest.mark.asyncio
    async def test_get_performance_metrics_success(self, stats_service):
        """Testa obtenção de métricas de performance com sucesso."""
        result = await stats_service.get_performance_metrics()
        
        assert result["operations"]["total"] == 6600
        assert result["operations"]["insert"] == 1000
        assert result["operations"]["query"] == 5000
        assert result["network"]["bytes_in"] == 1048576
        assert result["network"]["bytes_in_mb"] == 1.0
        assert result["network"]["bytes_out"] == 2097152
        assert result["network"]["bytes_out_mb"] == 2.0
        assert result["operations_per_hour"] == 275.0
    
    @pytest.mark.asyncio
    async def test_get_detailed_server_info_success(self, stats_service):
        """Testa obtenção de informações detalhadas do servidor com sucesso."""
        result = await stats_service.get_detailed_server_info()
        
        assert "server_status" in result
        assert "system_stats" in result
        assert "health_info" in result
        assert "performance_metrics" in result
        assert "summary" in result
        
        summary = result["summary"]
        assert summary["version"] == "7.0.0"
        assert summary["uptime_days"] == 1.0
        assert summary["databases_count"] == 5
        assert summary["total_collections"] == 25
        assert summary["total_objects"] == 10000
        assert summary["status"] == "healthy" 