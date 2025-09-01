"""
Dependency injection container for MongoDB tools.

This module provides a centralized way to manage dependencies
and avoid circular imports between modules.
"""

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.utils.mongo_connector import MongoDBConnector
    from mcp.server import FastMCP
    import structlog

# Global instances that will be initialized by the server
_mongo_connector: Optional["MongoDBConnector"] = None
_logger: Optional["structlog.BoundLogger"] = None
_server: Optional["FastMCP"] = None


class DependencyContainer:
    """Dependency injection container for tools."""
    
    @staticmethod
    def initialize(connector: "MongoDBConnector", logger: "structlog.BoundLogger", server: "FastMCP") -> None:
        """Initialize the dependency container."""
        global _mongo_connector, _logger, _server
        _mongo_connector = connector
        _logger = logger
        _server = server
    
    @staticmethod
    def get_mongo_connector() -> "MongoDBConnector":
        """Get the MongoDB connector instance."""
        if _mongo_connector is None:
            raise RuntimeError("MongoDB connector not initialized. Call DependencyContainer.initialize() first.")
        return _mongo_connector
    
    @staticmethod
    def get_logger() -> "structlog.BoundLogger":
        """Get the logger instance."""
        if _logger is None:
            raise RuntimeError("Logger not initialized. Call DependencyContainer.initialize() first.")
        return _logger
    
    @staticmethod
    def get_server() -> "FastMCP":
        """Get the FastMCP server instance."""
        if _server is None:
            raise RuntimeError("Server not initialized. Call DependencyContainer.initialize() first.")
        return _server
    
    @staticmethod
    def is_initialized() -> bool:
        """Check if the container is initialized."""
        return all([_mongo_connector is not None, _logger is not None, _server is not None])


# Convenience functions for backward compatibility
def get_mongo_connector() -> "MongoDBConnector":
    """Get the MongoDB connector instance."""
    return DependencyContainer.get_mongo_connector()


def get_logger() -> "structlog.BoundLogger":
    """Get the logger instance."""
    return DependencyContainer.get_logger()


def get_server() -> "FastMCP":
    """Get the FastMCP server instance."""
    return DependencyContainer.get_server() 