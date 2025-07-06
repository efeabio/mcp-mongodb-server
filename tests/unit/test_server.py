"""
Testes unitários para o servidor FastMCP.

Este módulo testa as tools FastMCP usando mocks para simular
os serviços e o MongoDB.
"""

import pytest
from unittest.mock import AsyncMock, patch
from src.server import (
    list_databases,
    get_database_info,
    list_collections,
    get_collection_info,
    get_server_status,
    get_system_stats
)
from src.core.exceptions import DatabaseNotFoundError, CollectionNotFoundError


class TestFastMCPServer:
    """Testes para o servidor FastMCP."""
    
    @pytest.mark.asyncio
    async def test_list_databases_success(self, database_service):
        """Testa tool list_databases com sucesso."""
        with patch('src.server.database_service', database_service):
            result = await list_databases()
        
        assert isinstance(result, dict)
        assert "databases" in result
        assert "total_count" in result
        assert "status" in result
        assert result["status"] == "success"
        assert isinstance(result["databases"], list)
        assert len(result["databases"]) == 1
        assert result["databases"][0]["name"] == "test_db"
    
    @pytest.mark.asyncio
    async def test_list_databases_error(self):
        """Testa tool list_databases com erro."""
        with patch('src.server.database_service') as mock_service:
            mock_service.list_databases.side_effect = Exception("Erro de conexão")
            
            result = await list_databases()
            
            assert isinstance(result, dict)
            assert "error" in result
            assert "status" in result
            assert result["status"] == "error"
            assert "Erro ao listar databases" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_database_info_success(self, database_service):
        """Testa tool get_database_info com sucesso."""
        with patch('src.server.database_service', database_service):
            result = await get_database_info("test_db")
        
        assert isinstance(result, dict)
        assert "database" in result
        assert "status" in result
        assert result["status"] == "success"
        assert result["database"]["name"] == "test_db"
        assert result["database"]["collections"] == 5
        assert result["database"]["objects"] == 1000
    
    @pytest.mark.asyncio
    async def test_get_database_info_validation_error(self):
        """Testa tool get_database_info com erro de validação."""
        with patch('src.server.database_service') as mock_service:
            mock_service.get_database_info.side_effect = ValueError("Nome inválido")
            
            result = await get_database_info("invalid_db")
            
            assert isinstance(result, dict)
            assert "error" in result
            assert "status" in result
            assert result["status"] == "error"
            assert "Erro de validação" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_database_info_not_found_error(self):
        """Testa tool get_database_info com database não encontrado."""
        with patch('src.server.database_service') as mock_service:
            mock_service.get_database_info.side_effect = DatabaseNotFoundError("Database não encontrado")
            
            result = await get_database_info("nonexistent_db")
            
            assert isinstance(result, dict)
            assert "error" in result
            assert "status" in result
            assert result["status"] == "error"
            assert "Database não encontrado" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_database_info_general_error(self):
        """Testa tool get_database_info com erro geral."""
        with patch('src.server.database_service') as mock_service:
            mock_service.get_database_info.side_effect = Exception("Erro geral")
            
            result = await get_database_info("test_db")
            
            assert isinstance(result, dict)
            assert "error" in result
            assert "status" in result
            assert result["status"] == "error"
            assert "Erro ao obter informações do database" in result["error"]
    
    @pytest.mark.asyncio
    async def test_list_collections_success(self, collection_service):
        """Testa tool list_collections com sucesso."""
        with patch('src.server.collection_service', collection_service):
            result = await list_collections("test_db")
        
        assert isinstance(result, dict)
        assert "database_name" in result
        assert "collections" in result
        assert "total_count" in result
        assert "status" in result
        assert result["status"] == "success"
        assert result["database_name"] == "test_db"
        assert isinstance(result["collections"], list)
        assert len(result["collections"]) == 1
        assert result["collections"][0]["name"] == "users"
    
    @pytest.mark.asyncio
    async def test_list_collections_validation_error(self):
        """Testa tool list_collections com erro de validação."""
        with patch('src.server.collection_service') as mock_service:
            mock_service.list_collections.side_effect = ValueError("Nome inválido")
            
            result = await list_collections("invalid_db")
            
            assert isinstance(result, dict)
            assert "error" in result
            assert "status" in result
            assert result["status"] == "error"
            assert "Erro de validação" in result["error"]
    
    @pytest.mark.asyncio
    async def test_list_collections_database_not_found_error(self):
        """Testa tool list_collections com database não encontrado."""
        with patch('src.server.collection_service') as mock_service:
            mock_service.list_collections.side_effect = DatabaseNotFoundError("Database não encontrado")
            
            result = await list_collections("nonexistent_db")
            
            assert isinstance(result, dict)
            assert "error" in result
            assert "status" in result
            assert result["status"] == "error"
            assert "Database não encontrado" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_collection_info_success(self, collection_service):
        """Testa tool get_collection_info com sucesso."""
        with patch('src.server.collection_service', collection_service):
            result = await get_collection_info("test_db", "users")
        
        assert isinstance(result, dict)
        assert "collection" in result
        assert "database_name" in result
        assert "status" in result
        assert result["status"] == "success"
        assert result["database_name"] == "test_db"
        assert result["collection"]["name"] == "users"
        assert result["collection"]["count"] == 500
        assert result["collection"]["size"] == 524288
    
    @pytest.mark.asyncio
    async def test_get_collection_info_validation_error(self):
        """Testa tool get_collection_info com erro de validação."""
        with patch('src.server.collection_service') as mock_service:
            mock_service.get_collection_info.side_effect = ValueError("Nome inválido")
            
            result = await get_collection_info("test_db", "invalid_collection")
            
            assert isinstance(result, dict)
            assert "error" in result
            assert "status" in result
            assert result["status"] == "error"
            assert "Erro de validação" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_collection_info_database_not_found_error(self):
        """Testa tool get_collection_info com database não encontrado."""
        with patch('src.server.collection_service') as mock_service:
            mock_service.get_collection_info.side_effect = DatabaseNotFoundError("Database não encontrado")
            
            result = await get_collection_info("nonexistent_db", "users")
            
            assert isinstance(result, dict)
            assert "error" in result
            assert "status" in result
            assert result["status"] == "error"
            assert "Database não encontrado" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_collection_info_collection_not_found_error(self):
        """Testa tool get_collection_info com collection não encontrada."""
        with patch('src.server.collection_service') as mock_service:
            mock_service.get_collection_info.side_effect = CollectionNotFoundError("Collection não encontrada")
            
            result = await get_collection_info("test_db", "nonexistent_collection")
            
            assert isinstance(result, dict)
            assert "error" in result
            assert "status" in result
            assert result["status"] == "error"
            assert "Collection não encontrada" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_server_status_success(self, stats_service):
        """Testa tool get_server_status com sucesso."""
        with patch('src.server.stats_service', stats_service):
            result = await get_server_status()
        
        assert isinstance(result, dict)
        assert "server_status" in result
        assert "status" in result
        assert result["status"] == "success"
        assert result["server_status"]["version"] == "7.0.0"
        assert result["server_status"]["uptime"] == 86400
        assert "connections" in result["server_status"]
        assert "memory" in result["server_status"]
        assert "operations" in result["server_status"]
        assert "network" in result["server_status"]
    
    @pytest.mark.asyncio
    async def test_get_server_status_error(self):
        """Testa tool get_server_status com erro."""
        with patch('src.server.stats_service') as mock_service:
            mock_service.get_server_status.side_effect = Exception("Erro de conexão")
            
            result = await get_server_status()
            
            assert isinstance(result, dict)
            assert "error" in result
            assert "status" in result
            assert result["status"] == "error"
            assert "Erro ao obter status do servidor" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_system_stats_success(self, stats_service):
        """Testa tool get_system_stats com sucesso."""
        with patch('src.server.stats_service', stats_service):
            result = await get_system_stats()
        
        assert isinstance(result, dict)
        assert "system_stats" in result
        assert "status" in result
        assert result["status"] == "success"
        assert result["system_stats"]["databases_count"] == 5
        assert result["system_stats"]["total_collections"] == 25
        assert result["system_stats"]["total_objects"] == 10000
    
    @pytest.mark.asyncio
    async def test_get_system_stats_error(self):
        """Testa tool get_system_stats com erro."""
        with patch('src.server.stats_service') as mock_service:
            mock_service.get_system_stats.side_effect = Exception("Erro de conexão")
            
            result = await get_system_stats()
            
            assert isinstance(result, dict)
            assert "error" in result
            assert "status" in result
            assert result["status"] == "error"
            assert "Erro ao obter estatísticas do sistema" in result["error"]
    
    @pytest.mark.asyncio
    async def test_all_tools_return_dict(self, database_service, collection_service, stats_service):
        """Testa se todas as tools retornam dicionários."""
        with patch('src.server.database_service', database_service), \
             patch('src.server.collection_service', collection_service), \
             patch('src.server.stats_service', stats_service):
            tools = [
                list_databases(),
                get_database_info("test_db"),
                list_collections("test_db"),
                get_collection_info("test_db", "users"),
                get_server_status(),
                get_system_stats()
            ]
            # Aguarda todas as corrotinas
            results = [await tool for tool in tools]
        for tool_result in results:
            assert isinstance(tool_result, dict)
            assert "status" in tool_result
    
    @pytest.mark.asyncio
    async def test_error_handling_consistency(self):
        """Testa consistência no tratamento de erros."""
        with patch('src.server.database_service') as mock_service:
            mock_service.list_databases.side_effect = Exception("Erro de teste")
            
            result = await list_databases()
            
            # Verifica estrutura consistente de erro
            assert "error" in result
            assert "status" in result
            assert result["status"] == "error"
            assert isinstance(result["error"], str)
            assert len(result["error"]) > 0 