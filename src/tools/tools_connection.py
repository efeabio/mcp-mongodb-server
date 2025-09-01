"""
Tools for MongoDB connection management.

This module contains tools for configuring and managing dynamic
connections to MongoDB, allowing AI to configure connections as needed.
"""

from typing import Dict, Any, Optional
import asyncio

from src.utils.mongo_connector import MongoDBConnector
from src.utils.security import sanitize_connection_params, sanitize_uri, SecureLoggerAdapter
from src.core.exceptions import MongoDBConnectionError
from .dependencies import DependencyContainer
from .decorators import mongodb_tool

# Global connection status
_connection_status = {
    "connected": False,
    "uri": None,
    "error": None
}

# Store the current connector separately for connection management
_current_connector: Optional[MongoDBConnector] = None

@mongodb_tool(
    name="mongodb_configure_connection",
    description="Configure a new MongoDB connection",
    requires_connection=False
)
async def configure_mongodb_connection(
    host: str = "localhost",
    port: int = 27017,
    username: Optional[str] = None,
    password: Optional[str] = None,
    auth_source: str = "admin",
    database: Optional[str] = None,
    max_connections: int = 10
) -> Dict[str, Any]:
    """
    Configure a new MongoDB connection.
    
    This tool allows the AI to configure a MongoDB connection
    by providing the necessary parameters.
    
    Args:
        host: MongoDB server host (default: localhost)
        port: MongoDB server port (default: 27017)
        username: Username for authentication (optional)
        password: Password for authentication (optional)
        auth_source: Authentication database (default: admin)
        database: Specific database to connect to (optional)
        max_connections: Maximum connections in pool (default: 10)
    
    Returns:
        Dictionary with connection status and server information
    """
    global _current_connector, _connection_status
    
    try:
        # Get logger and sanitize connection params for logging
        logger = DependencyContainer.get_logger()
        secure_logger = SecureLoggerAdapter(logger)
        
        connection_params = {
            'host': host,
            'port': port,
            'username': username,
            'password': password,
            'auth_source': auth_source,
            'database': database,
            'max_connections': max_connections
        }
        
        sanitized_params = sanitize_connection_params(connection_params)
        secure_logger.info("Configuring new MongoDB connection", **sanitized_params)
        
        # Build connection URI
        if username and password:
            uri = f"mongodb://{username}:{password}@{host}:{port}"
            if auth_source:
                uri += f"/?authSource={auth_source}"
        else:
            uri = f"mongodb://{host}:{port}"
            if database:
                uri += f"/{database}"
        
        # Close previous connection if exists
        if _current_connector:
            try:
                _current_connector.close()
            except Exception:
                pass
        
        # Create new connection
        _current_connector = MongoDBConnector(uri, max_connections)
        
        # Update the dependency container with the new connector
        DependencyContainer.initialize(
            _current_connector,
            logger,
            DependencyContainer.get_server()
        )
        
        # Test the connection
        test_result = await test_connection()
        if test_result.get("status") != "success":
            return test_result
        
        # Update status
        _connection_status.update({
            "connected": True,
            "uri": sanitize_uri(uri),  # Store sanitized URI
            "error": None
        })
        
        # Get server information
        server_info = await get_server_info()
        
        return {
            "success": True,
            "message": "MongoDB connection configured successfully",
            "connection": sanitize_connection_params({
                "host": host,
                "port": port,
                "username": username,
                "auth_source": auth_source,
                "database": database,
                "max_connections": max_connections
            }),
            "server_info": server_info
        }
        
    except Exception as e:
        error_msg = f"Failed to configure MongoDB connection: {str(e)}"
        logger = DependencyContainer.get_logger()
        logger.error("MongoDB connection configuration failed", error=str(e))
        
        _connection_status.update({
            "connected": False,
            "uri": None,
            "error": error_msg
        })
        
        return {
            "success": False,
            "error": error_msg
        }

@mongodb_tool(
    name="mongodb_test_connection",
    description="Test the current MongoDB connection",
    requires_connection=False
)
async def test_connection() -> Dict[str, Any]:
    """
    Test the current MongoDB connection.
    
    Returns:
        Dictionary with connection status
    """
    global _current_connector, _connection_status
    
    try:
        if not _current_connector:
            return {
                "success": False,
                "error": "No connection configured. Use configure_mongodb_connection first."
            }
        
        # Test ping
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            _current_connector._executor,
            _current_connector.client.admin.command,
            'ping'
        )
        
        # Get server information
        server_info = await get_server_info()
        
        _connection_status["connected"] = True
        _connection_status["error"] = None
        
        return {
            "success": True,
            "status": "success",
            "message": "MongoDB connection is active",
            "server_info": server_info
        }
        
    except Exception as e:
        error_msg = f"MongoDB connection error: {str(e)}"
        logger = DependencyContainer.get_logger()
        logger.error("MongoDB connection test failed", error=str(e))
        
        _connection_status["connected"] = False
        _connection_status["error"] = error_msg
        
        return {
            "success": False,
            "status": "error",
            "error": error_msg
        }

@mongodb_tool(
    name="mongodb_get_connection_status",
    description="Get the current MongoDB connection status",
    requires_connection=False
)
async def get_connection_status() -> Dict[str, Any]:
    """
    Get the current MongoDB connection status.
    
    Returns:
        Dictionary with connection status
    """
    global _connection_status, _current_connector
    
    if not _current_connector:
        return {
            "success": False,
            "error": "No connection configured. Use configure_mongodb_connection first."
        }
    
    # Test current connection
    test_result = await test_connection()
    
    return {
        "success": True,
        "connection_status": _connection_status,
        "test_result": test_result
    }

async def get_server_info() -> Dict[str, Any]:
    """
    Get basic MongoDB server information.
    
    Returns:
        Dictionary with server information
    """
    global _current_connector
    
    try:
        if not _current_connector:
            return {
                "success": False,
                "error": "No connection configured"
            }
        
        loop = asyncio.get_event_loop()
        
        # Get server information
        server_info = await loop.run_in_executor(
            _current_connector._executor,
            _current_connector.client.admin.command,
            'serverStatus'
        )
        
        # Get list of databases
        databases = await loop.run_in_executor(
            _current_connector._executor,
            _current_connector.client.list_database_names
        )
        
        # Filter system databases
        user_databases = [name for name in databases if name not in ['admin', 'local', 'config']]
        
        return {
            "success": True,
            "server": {
                "version": server_info.get('version', ''),
                "uptime": server_info.get('uptime', 0),
                "connections": server_info.get('connections', {}),
                "memory": server_info.get('mem', {}),
                "operations": server_info.get('opcounters', {})
            },
            "databases": {
                "total": len(databases),
                "user_databases": len(user_databases),
                "system_databases": len(databases) - len(user_databases)
            }
        }
        
    except Exception as e:
        error_msg = f"Failed to get server information: {str(e)}"
        try:
            logger = DependencyContainer.get_logger()
            logger.error("Failed to get server information", error=str(e))
        except:
            pass  # Logger not available
        
        return {
            "success": False,
            "error": error_msg
        }

@mongodb_tool(
    name="mongodb_disconnect",
    description="Disconnect from MongoDB and cleanup resources",
    requires_connection=False
)
async def disconnect_mongodb() -> Dict[str, Any]:
    """
    Disconnect from MongoDB and cleanup resources.
    
    Returns:
        Dictionary with disconnection status
    """
    global _current_connector, _connection_status
    
    try:
        if _current_connector:
            _current_connector.close()
            _current_connector = None
        
        _connection_status.update({
            "connected": False,
            "uri": None,
            "error": None
        })
        
        try:
            logger = DependencyContainer.get_logger()
            logger.info("Successfully disconnected from MongoDB")
        except:
            pass  # Logger not available
        
        return {
            "success": True,
            "message": "Successfully disconnected from MongoDB"
        }
        
    except Exception as e:
        error_msg = f"Failed to disconnect from MongoDB: {str(e)}"
        try:
            logger = DependencyContainer.get_logger()
            logger.error("Failed to disconnect from MongoDB", error=str(e))
        except:
            pass  # Logger not available
        
        return {
            "success": False,
            "error": error_msg
        }

def get_mongo_connector() -> Optional[MongoDBConnector]:
    """
    Get the current MongoDB connector.
    
    Returns:
        MongoDBConnector or None if no connection
    """
    return _current_connector


def is_connected() -> bool:
    """
    Check if there is an active MongoDB connection.
    
    Returns:
        True if connected, False otherwise
    """
    return _connection_status["connected"] and _current_connector is not None


def initialize_tools_connection(mongo_connector, logger, server):
    """
    Initialize tools_connection module.
    This function exists to maintain compatibility with the server initialization.
    The actual tools are registered via decorators.
    """
    # The DependencyContainer is initialized when a connection is configured
    # This function is kept for compatibility with the server initialization pattern
    pass
