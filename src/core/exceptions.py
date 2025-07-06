"""
Exceções customizadas do FastMCP MongoDB Server.

Este módulo contém todas as exceções específicas do projeto
para tratamento adequado de erros.
"""


class FastMCPMongoDBError(Exception):
    """
    Exceção base para erros do FastMCP MongoDB Server.
    
    Esta é a exceção base para todos os erros específicos do projeto.
    """
    pass


class MongoDBConnectionError(FastMCPMongoDBError):
    """
    Erro de conexão com MongoDB.
    
    Levantada quando não é possível conectar ao servidor MongoDB.
    """
    pass


class DatabaseNotFoundError(FastMCPMongoDBError):
    """
    Database não encontrado.
    
    Levantada quando um database específico não existe no MongoDB.
    """
    pass


class CollectionNotFoundError(FastMCPMongoDBError):
    """
    Collection não encontrada.
    
    Levantada quando uma collection específica não existe no database.
    """
    pass


class InvalidQueryError(FastMCPMongoDBError):
    """
    Query inválida.
    
    Levantada quando uma query para o MongoDB é inválida.
    """
    pass


class AuthenticationError(FastMCPMongoDBError):
    """
    Erro de autenticação.
    
    Levantada quando há problemas de autenticação com o MongoDB.
    """
    pass


class TimeoutError(FastMCPMongoDBError):
    """
    Erro de timeout.
    
    Levantada quando uma operação excede o tempo limite.
    """
    pass


class ConfigurationError(FastMCPMongoDBError):
    """
    Erro de configuração.
    
    Levantada quando há problemas com as configurações do servidor.
    """
    pass 