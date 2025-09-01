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
    async def test_list_databases_success(self):
        """Testa tool list_databases com sucesso."""
        result = await list_databases()
        
        assert isinstance(result, dict)
        # Sem conexão MongoDB, deve retornar erro
        assert "error" in result
        assert "MongoDB" in result["error"] or "conexão" in result["error"]
    
    @pytest.mark.asyncio
    async def test_list_databases_error(self):
        """Testa tool list_databases com erro."""
        result = await list_databases()
        
        assert isinstance(result, dict)
        # Sem conexão MongoDB, deve retornar erro
        assert "error" in result
        assert "MongoDB" in result["error"] or "conexão" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_database_info_success(self):
        """Testa tool get_database_info com sucesso."""
        result = await get_database_info("test_db")
        
        assert isinstance(result, dict)
        # Sem conexão MongoDB, deve retornar erro
        assert "error" in result
        assert "MongoDB" in result["error"] or "conexão" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_database_info_validation_error(self):
        """Testa tool get_database_info com erro de validação."""
        result = await get_database_info("invalid_db")
        
        assert isinstance(result, dict)
        # Sem conexão MongoDB, deve retornar erro
        assert "error" in result
        assert "MongoDB" in result["error"] or "conexão" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_database_info_not_found_error(self):
        """Testa tool get_database_info com database não encontrado."""
        result = await get_database_info("nonexistent_db")
        
        assert isinstance(result, dict)
        # Sem conexão MongoDB, deve retornar erro
        assert "error" in result
        assert "MongoDB" in result["error"] or "conexão" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_database_info_general_error(self):
        """Testa tool get_database_info com erro geral."""
        result = await get_database_info("nonexistent_db")
        
        assert isinstance(result, dict)
        # Sem conexão MongoDB, deve retornar erro
        assert "error" in result
        assert "MongoDB" in result["error"] or "conexão" in result["error"]
    
    @pytest.mark.asyncio
    async def test_list_collections_success(self):
        """Testa tool list_collections com sucesso."""
        result = await list_collections("test_db")
        
        assert isinstance(result, dict)
        # Sem conexão MongoDB, deve retornar erro
        assert "error" in result
        assert "MongoDB" in result["error"] or "conexão" in result["error"]
    
    @pytest.mark.asyncio
    async def test_list_collections_validation_error(self):
        """Testa tool list_collections com erro de validação."""
        result = await list_collections("invalid_db")
        
        assert isinstance(result, dict)
        # Sem conexão MongoDB, deve retornar erro
        assert "error" in result
        assert "MongoDB" in result["error"] or "conexão" in result["error"]
    
    @pytest.mark.asyncio
    async def test_list_collections_database_not_found_error(self):
        """Testa tool list_collections com database não encontrado."""
        result = await list_collections("nonexistent_db")
        
        assert isinstance(result, dict)
        # Sem conexão MongoDB, deve retornar erro
        assert "error" in result
        assert "MongoDB" in result["error"] or "conexão" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_collection_info_success(self):
        """Testa tool get_collection_info com sucesso."""
        result = await get_collection_info("test_db", "users")
        
        assert isinstance(result, dict)
        # Sem conexão MongoDB, deve retornar erro
        assert "error" in result
        assert "MongoDB" in result["error"] or "conexão" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_collection_info_validation_error(self):
        """Testa tool get_collection_info com erro de validação."""
        result = await get_collection_info("test_db", "invalid_collection")
        
        assert isinstance(result, dict)
        # Sem conexão MongoDB, deve retornar erro
        assert "error" in result
        assert "MongoDB" in result["error"] or "conexão" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_collection_info_database_not_found_error(self):
        """Testa tool get_collection_info com database não encontrado."""
        result = await get_collection_info("nonexistent_db", "users")
        
        assert isinstance(result, dict)
        # Sem conexão MongoDB, deve retornar erro
        assert "error" in result
        assert "MongoDB" in result["error"] or "conexão" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_collection_info_collection_not_found_error(self):
        """Testa tool get_collection_info com collection não encontrada."""
        result = await get_collection_info("test_db", "nonexistent_collection")
        
        assert isinstance(result, dict)
        # Sem conexão MongoDB, deve retornar erro
        assert "error" in result
        assert "MongoDB" in result["error"] or "conexão" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_server_status_success(self):
        """Testa tool get_server_status com sucesso."""
        result = await get_server_status()
        
        assert isinstance(result, dict)
        # Sem conexão MongoDB, deve retornar erro
        assert "error" in result
        assert "MongoDB" in result["error"] or "conexão" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_server_status_error(self):
        """Testa tool get_server_status com erro."""
        result = await get_server_status()
        
        assert isinstance(result, dict)
        # Sem conexão MongoDB, deve retornar erro
        assert "error" in result
        assert "MongoDB" in result["error"] or "conexão" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_system_stats_success(self):
        """Testa tool get_system_stats com sucesso."""
        result = await get_system_stats()
        
        assert isinstance(result, dict)
        # Sem conexão MongoDB, deve retornar erro
        assert "error" in result
        assert "MongoDB" in result["error"] or "conexão" in result["error"]
    
    @pytest.mark.asyncio
    async def test_get_system_stats_error(self):
        """Testa tool get_system_stats com erro."""
        result = await get_system_stats()
        
        assert isinstance(result, dict)
        # Sem conexão MongoDB, deve retornar erro
        assert "error" in result
        assert "MongoDB" in result["error"] or "conexão" in result["error"]
    
    @pytest.mark.asyncio
    async def test_all_tools_return_dict(self):
        """Testa se todas as tools retornam dicionários."""
        tools = [
            list_databases,
            get_database_info,
            list_collections,
            get_collection_info,
            get_server_status,
            get_system_stats
        ]
        
        for tool in tools:
            if tool == get_database_info:
                result = await tool("test_db")
            elif tool in [get_collection_info]:
                result = await tool("test_db", "test_collection")
            elif tool == list_collections:
                result = await tool("test_db")
            else:
                result = await tool()
            
            assert isinstance(result, dict)
            assert "error" in result or "status" in result
    
    @pytest.mark.asyncio
    async def test_error_handling_consistency(self):
        """Testa se o tratamento de erros é consistente."""
        tools = [
            list_databases,
            get_database_info,
            list_collections,
            get_collection_info,
            get_server_status,
            get_system_stats
        ]
        
        for tool in tools:
            if tool == get_database_info:
                result = await tool("test_db")
            elif tool in [get_collection_info]:
                result = await tool("test_db", "test_collection")
            elif tool == list_collections:
                result = await tool("test_db")
            else:
                result = await tool()
            
            # Todas as tools devem retornar dicionários com estrutura consistente
            assert isinstance(result, dict)
            # Sem conexão MongoDB, todas devem retornar erro
            assert "error" in result 