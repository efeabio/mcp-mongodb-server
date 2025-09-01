"""
Testes unitários para utilitários e configurações do FastMCP MongoDB Server.

Este módulo testa os utilitários, configurações e exceções.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.utils.security import (
    sanitize_uri,
    sanitize_log_data,
    mask_string,
    sanitize_connection_params,
    is_sensitive_field,
    SecureLoggerAdapter
)
from src.utils.logger import (
    setup_logging,
    get_logger,
    configure_logging_for_tests
)
from src.config.settings import Settings
from src.core.exceptions import (
    FastMCPMongoDBError,
    MongoDBConnectionError,
    DatabaseNotFoundError,
    CollectionNotFoundError,
    InvalidQueryError,
    AuthenticationError,
    TimeoutError,
    ConfigurationError
)


class TestSecurityUtils:
    """Testes para utilitários de segurança."""
    
    def test_sanitize_uri_with_password(self):
        """Testa sanitização de URI com senha."""
        uri = "mongodb://user:password123@localhost:27017/db"
        sanitized = sanitize_uri(uri)
        
        assert sanitized == "mongodb://user:***@localhost:27017/db"
        assert "password123" not in sanitized
        assert "***" in sanitized
    
    def test_sanitize_uri_without_password(self):
        """Testa sanitização de URI sem senha."""
        uri = "mongodb://localhost:27017/db"
        sanitized = sanitize_uri(uri)
        
        assert sanitized == uri
    
    def test_sanitize_uri_invalid_format(self):
        """Testa sanitização de URI com formato inválido."""
        uri = "invalid://uri:format"
        sanitized = sanitize_uri(uri)
        
        # Deve retornar a URI original se falhar
        assert sanitized == uri
    
    def test_sanitize_log_data_password(self):
        """Testa sanitização de dados de log com senha."""
        data = {
            "username": "test_user",
            "password": "secret123",
            "host": "localhost"
        }
        sanitized = sanitize_log_data(data)
        
        assert sanitized["username"] == "test_user"  # Username não é mascarado
        assert sanitized["password"] == "***"
        assert sanitized["host"] == "localhost"
    
    def test_sanitize_log_data_uri(self):
        """Testa sanitização de dados de log com URI."""
        data = {
            "connection_string": "mongodb://user:pass@localhost:27017",
            "other_data": "normal"
        }
        sanitized = sanitize_log_data(data)
        
        # URI não é sanitizada automaticamente
        assert sanitized["connection_string"] == "mongodb://user:pass@localhost:27017"
        assert sanitized["other_data"] == "normal"
    
    def test_sanitize_log_data_nested(self):
        """Testa sanitização de dados aninhados."""
        data = {
            "config": {
                "credentials": {
                    "password": "secret",
                    "api_key": "key123"
                }
            },
            "normal_field": "value"
        }
        sanitized = sanitize_log_data(data)
        
        # Dados aninhados são sanitizados
        assert isinstance(sanitized, dict)
        # Verifica se os campos sensíveis foram mascarados
        assert sanitized["config"]["credentials"] == "[MASKED]"
        assert sanitized["normal_field"] == "value"
    
    def test_mask_string_long(self):
        """Testa mascaramento de string longa."""
        masked = mask_string("password123", 3)
        assert masked == "pas***"
    
    def test_mask_string_short(self):
        """Testa mascaramento de string curta."""
        masked = mask_string("ab", 3)
        assert masked == "***"
    
    def test_mask_string_empty(self):
        """Testa mascaramento de string vazia."""
        masked = mask_string("", 3)
        assert masked == "***"
    
    def test_sanitize_connection_params(self):
        """Testa sanitização de parâmetros de conexão."""
        params = {
            "host": "localhost",
            "username": "testuser",
            "password": "secret123",
            "port": 27017
        }
        sanitized = sanitize_connection_params(params)
        
        assert sanitized["host"] == "localhost"
        assert sanitized["username"] == "te***"
        assert sanitized["password"] == "sec***"
        assert sanitized["port"] == 27017
    
    def test_is_sensitive_field(self):
        """Testa identificação de campos sensíveis."""
        sensitive_fields = ["password", "api_key", "secret", "token"]
        normal_fields = ["host", "port", "database", "collection"]
        
        for field in sensitive_fields:
            assert is_sensitive_field(field) is True
        
        for field in normal_fields:
            assert is_sensitive_field(field) is False


class TestSecureLoggerAdapter:
    """Testes para o adaptador de logger seguro."""
    
    def test_secure_logger_adapter(self):
        """Testa o adaptador de logger seguro."""
        mock_logger = MagicMock()
        secure_logger = SecureLoggerAdapter(mock_logger)
        
        # Testa logging com dados sensíveis
        secure_logger.info("Test message", password="secret123", username="test")
        
        # Verifica se o logger foi chamado
        mock_logger.info.assert_called_once()
        
        # Verifica se os dados sensíveis foram sanitizados
        call_args = mock_logger.info.call_args
        assert "password" in call_args[1]
        assert call_args[1]["password"] == "***"
        assert call_args[1]["username"] == "test"


class TestLogger:
    """Testes para o sistema de logging."""
    
    def test_get_logger(self):
        """Testa obtenção de logger."""
        logger = get_logger("test_module")
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "debug")
    
    def test_configure_logging_for_tests(self):
        """Testa configuração de logging para testes."""
        # Não deve falhar
        configure_logging_for_tests()


class TestSettings:
    """Testes para as configurações."""
    
    def test_settings_defaults(self):
        """Testa valores padrão das configurações."""
        settings = Settings()
        
        assert settings.mongodb_uri == "mongodb://localhost:27017"
        assert settings.mongodb_auth_source == "admin"
        assert settings.fastmcp_server_name == "mongodb-info-server"
        assert settings.fastmcp_server_version == "1.0.0"
        assert settings.log_level == "INFO"
    
    def test_settings_custom_values(self):
        """Testa configurações com valores customizados."""
        settings = Settings(
            mongodb_uri="mongodb://custom:27017",
            mongodb_username="custom_user",
            log_level="DEBUG"
        )
        
        assert settings.mongodb_uri == "mongodb://custom:27017"
        assert settings.mongodb_username == "custom_user"
        assert settings.log_level == "DEBUG"


class TestExceptions:
    """Testes para as exceções customizadas."""
    
    def test_exception_inheritance(self):
        """Testa hierarquia de exceções."""
        # Todas devem herdar da exceção base
        assert issubclass(MongoDBConnectionError, FastMCPMongoDBError)
        assert issubclass(DatabaseNotFoundError, FastMCPMongoDBError)
        assert issubclass(CollectionNotFoundError, FastMCPMongoDBError)
        assert issubclass(InvalidQueryError, FastMCPMongoDBError)
        assert issubclass(AuthenticationError, FastMCPMongoDBError)
        assert issubclass(TimeoutError, FastMCPMongoDBError)
        assert issubclass(ConfigurationError, FastMCPMongoDBError)
    
    def test_exception_messages(self):
        """Testa mensagens das exceções."""
        message = "Test error message"
        
        conn_error = MongoDBConnectionError(message)
        db_error = DatabaseNotFoundError(message)
        coll_error = CollectionNotFoundError(message)
        
        assert str(conn_error) == message
        assert str(db_error) == message
        assert str(coll_error) == message
    
    def test_exception_creation(self):
        """Testa criação de exceções."""
        # Deve ser possível criar exceções sem argumentos
        try:
            raise FastMCPMongoDBError()
        except FastMCPMongoDBError:
            pass
        
        try:
            raise MongoDBConnectionError()
        except MongoDBConnectionError:
            pass


class TestModels:
    """Testes para os modelos Pydantic."""
    
    def test_database_info_validation(self):
        """Testa validação de DatabaseInfo."""
        from src.models.schemas import DatabaseInfo
        
        # Teste com dados válidos
        db_info = DatabaseInfo(
            name="test_db",
            size_on_disk=1024,
            collections=5,
            objects=100,
            data_size=1024,
            storage_size=2048,
            indexes=2,
            index_size=512
        )
        
        assert db_info.name == "test_db"
        assert db_info.size_on_disk == 1024
        assert db_info.collections == 5
    
    def test_database_info_invalid_name(self):
        """Testa validação de nome inválido."""
        from src.models.schemas import DatabaseInfo
        
        # Nome muito longo
        with pytest.raises(ValueError):
            DatabaseInfo(
                name="a" * 65,  # 65 caracteres (máximo é 64)
                size_on_disk=1024,
                collections=5,
                objects=100,
                data_size=1024,
                storage_size=2048,
                indexes=2,
                index_size=512
            )
    
    def test_collection_info_validation(self):
        """Testa validação de CollectionInfo."""
        from src.models.schemas import CollectionInfo
        
        # Teste com dados válidos
        coll_info = CollectionInfo(
            name="test_collection",
            count=100,
            size=1024,
            storage_size=2048,
            total_index_size=512,
            indexes=[]
        )
        
        assert coll_info.name == "test_collection"
        assert coll_info.count == 100
        assert coll_info.size == 1024
    
    def test_collection_info_invalid_name(self):
        """Testa validação de nome inválido de collection."""
        from src.models.schemas import CollectionInfo
        
        # Nome muito longo
        with pytest.raises(ValueError):
            CollectionInfo(
                name="a" * 256,  # 256 caracteres (máximo é 255)
                count=100,
                size=1024,
                storage_size=2048,
                total_index_size=512,
                indexes=[]
            )
    
    def test_database_query_validation(self):
        """Testa validação de DatabaseQuery."""
        from src.models.schemas import DatabaseQuery
        
        # Teste com dados válidos
        query = DatabaseQuery(database_name="test_db", limit=50)
        assert query.database_name == "test_db"
        assert query.limit == 50
    
    def test_database_query_invalid_limit(self):
        """Testa validação de limite inválido."""
        from src.models.schemas import DatabaseQuery
        
        # Limite inválido
        with pytest.raises(ValueError):
            DatabaseQuery(database_name="test_db", limit=0)
        
        with pytest.raises(ValueError):
            DatabaseQuery(database_name="test_db", limit=1001)
    
    def test_collection_query_validation(self):
        """Testa validação de CollectionQuery."""
        from src.models.schemas import CollectionQuery
        
        # Teste com dados válidos
        query = CollectionQuery(
            database_name="test_db",
            collection_name="test_collection",
            limit=50
        )
        assert query.database_name == "test_db"
        assert query.collection_name == "test_collection"
        assert query.limit == 50
