"""
Tool decorators and registry for MongoDB FastMCP tools.

This module provides decorators for automatic tool discovery and registration.
"""

from functools import wraps
from typing import Callable, Dict, Any, List
from .dependencies import DependencyContainer


class ToolRegistry:
    """Registry for MongoDB tools."""
    
    _tools: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def register_tool(
        cls, 
        name: str, 
        func: Callable, 
        description: str = "",
        requires_connection: bool = True
    ) -> None:
        """Register a tool in the registry."""
        cls._tools[name] = {
            'function': func,
            'description': description,
            'requires_connection': requires_connection,
            'name': name
        }
    
    @classmethod
    def get_tools(cls) -> Dict[str, Dict[str, Any]]:
        """Get all registered tools."""
        return cls._tools.copy()
    
    @classmethod
    def clear(cls) -> None:
        """Clear the registry (mainly for testing)."""
        cls._tools.clear()


def mongodb_tool(
    name: str = None,
    description: str = "",
    requires_connection: bool = True
):
    """
    Decorator to register a function as a MongoDB tool.
    
    Args:
        name: Tool name (defaults to function name)
        description: Tool description
        requires_connection: Whether the tool requires a MongoDB connection
    """
    def decorator(func: Callable) -> Callable:
        tool_name = name or func.__name__
        
        if requires_connection:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Check if connection is available
                if not DependencyContainer.is_initialized():
                    return {
                        "success": False,
                        "error": "MongoDB connection not configured. Please run 'configure_mongodb_connection' first.",
                        "suggestion": "Use the 'configure_mongodb_connection' tool to set up your MongoDB connection."
                    }
                
                try:
                    connector = DependencyContainer.get_mongo_connector()
                    if connector is None:
                        return {
                            "success": False,
                            "error": "MongoDB connection not available.",
                            "suggestion": "Use the 'configure_mongodb_connection' tool to establish a connection."
                        }
                    
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger = DependencyContainer.get_logger()
                    logger.error("Tool execution failed", tool=tool_name, error=str(e))
                    return {
                        "success": False,
                        "error": f"Tool execution failed: {str(e)}",
                        "tool": tool_name
                    }
        else:
            wrapper = func
        
        # Register the tool
        ToolRegistry.register_tool(
            name=tool_name,
            func=wrapper,
            description=description,
            requires_connection=requires_connection
        )
        
        return wrapper
    
    return decorator


def require_connection(func: Callable) -> Callable:
    """
    Decorator to ensure MongoDB connection is available.
    
    This is a standalone decorator that can be used with or without @mongodb_tool.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not DependencyContainer.is_initialized():
            return {
                "success": False,
                "error": "MongoDB connection not configured. Please run 'configure_mongodb_connection' first.",
                "suggestion": "Use the 'configure_mongodb_connection' tool to set up your MongoDB connection."
            }
        
        try:
            connector = DependencyContainer.get_mongo_connector()
            if connector is None:
                return {
                    "success": False,
                    "error": "MongoDB connection not available.",
                    "suggestion": "Use the 'configure_mongodb_connection' tool to establish a connection."
                }
            
            return await func(*args, **kwargs)
        except Exception as e:
            logger = DependencyContainer.get_logger()
            logger.error("Tool execution failed", tool=func.__name__, error=str(e))
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}",
                "tool": func.__name__
            }
    
    return wrapper


def register_tools_with_server():
    """Register all tools with the FastMCP server."""
    server = DependencyContainer.get_server()
    tools = ToolRegistry.get_tools()
    
    for tool_name, tool_info in tools.items():
        # Register the tool with the server
        server.tool(name=tool_name)(tool_info['function'])


def get_registered_tools() -> List[str]:
    """Get a list of all registered tool names."""
    return list(ToolRegistry.get_tools().keys())