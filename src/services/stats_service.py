"""
Serviço de Estatísticas para o FastMCP MongoDB Server.

Este módulo contém os serviços relacionados a estatísticas do MongoDB,
incluindo status do servidor e estatísticas do sistema.
"""

from typing import Dict, Any
from src.utils.mongo_connector import MongoDBConnector
from src.models.schemas import ServerStatus
from src.core.exceptions import MongoDBConnectionError
from src.utils.logger import get_logger


class StatsService:
    """
    Serviço para operações relacionadas a estatísticas do MongoDB.
    
    Fornece métodos para obter status do servidor e estatísticas do sistema,
    incluindo validação de entrada e tratamento de erros.
    """
    
    def __init__(self, mongo_connector: MongoDBConnector):
        """
        Inicializa o serviço de estatísticas.
        
        Args:
            mongo_connector: Instância do conector MongoDB
        """
        self.mongo_connector = mongo_connector
        self.logger = get_logger(__name__)
    
    async def get_server_status(self) -> ServerStatus:
        """
        Retorna status geral do servidor MongoDB.
        
        Returns:
            ServerStatus: Status detalhado do servidor
            
        Raises:
            MongoDBConnectionError: Se não conseguir conectar ao MongoDB
        """
        try:
            self.logger.info("Obtendo status do servidor MongoDB")
            
            server_status = await self.mongo_connector.get_server_status()
            
            self.logger.info("Status do servidor obtido com sucesso", 
                           version=server_status.version)
            return server_status
            
        except Exception as e:
            self.logger.error("Erro no serviço ao obter status do servidor", error=str(e))
            raise
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do sistema.
        
        Returns:
            Dicionário com estatísticas do sistema
            
        Raises:
            MongoDBConnectionError: Se não conseguir conectar ao MongoDB
        """
        try:
            self.logger.info("Obtendo estatísticas do sistema")
            
            system_stats = await self.mongo_connector.get_system_stats()
            
            self.logger.info("Estatísticas do sistema obtidas com sucesso", 
                           databases_count=system_stats.get('databases_count', 0))
            return system_stats
            
        except Exception as e:
            self.logger.error("Erro no serviço ao obter estatísticas do sistema", error=str(e))
            raise
    
    async def get_server_health(self) -> Dict[str, Any]:
        """
        Retorna informações de saúde do servidor.
        
        Returns:
            Dicionário com informações de saúde do servidor
            
        Raises:
            MongoDBConnectionError: Se não conseguir conectar ao MongoDB
        """
        try:
            self.logger.info("Verificando saúde do servidor")
            
            # Obtém status do servidor
            server_status = await self.get_server_status()
            
            # Calcula métricas de saúde
            uptime_hours = server_status.uptime / 3600
            uptime_days = uptime_hours / 24
            
            # Analisa conexões
            connections = server_status.connections
            current_connections = connections.get('current', 0)
            available_connections = connections.get('available', 0)
            total_connections = current_connections + available_connections
            
            # Analisa memória
            memory = server_status.memory
            memory_mb = memory.get('resident', 0) / 1024 / 1024
            memory_gb = memory_mb / 1024
            
            # Analisa operações
            operations = server_status.operations
            total_operations = sum(operations.values()) if operations else 0
            
            health_info = {
                "status": "healthy",
                "version": server_status.version,
                "uptime_seconds": server_status.uptime,
                "uptime_hours": round(uptime_hours, 2),
                "uptime_days": round(uptime_days, 2),
                "connections": {
                    "current": current_connections,
                    "available": available_connections,
                    "total": total_connections,
                    "usage_percentage": round((current_connections / total_connections * 100), 2) if total_connections > 0 else 0
                },
                "memory": {
                    "resident_mb": round(memory_mb, 2),
                    "resident_gb": round(memory_gb, 2),
                    "virtual_mb": round(memory.get('virtual', 0) / 1024 / 1024, 2),
                    "mapped_mb": round(memory.get('mapped', 0) / 1024 / 1024, 2)
                },
                "operations": {
                    "total": total_operations,
                    "details": operations
                },
                "network": server_status.network
            }
            
            self.logger.info("Informações de saúde do servidor obtidas com sucesso", 
                           status=health_info["status"])
            return health_info
            
        except Exception as e:
            self.logger.error("Erro ao obter informações de saúde do servidor", error=str(e))
            raise
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Retorna métricas de performance do servidor.
        
        Returns:
            Dicionário com métricas de performance
            
        Raises:
            MongoDBConnectionError: Se não conseguir conectar ao MongoDB
        """
        try:
            self.logger.info("Obtendo métricas de performance")
            
            # Obtém status do servidor
            server_status = await self.get_server_status()
            
            # Calcula métricas de performance
            operations = server_status.operations
            network = server_status.network
            
            # Calcula throughput de operações
            total_ops = sum(operations.values()) if operations else 0
            
            # Calcula métricas de rede
            bytes_in = network.get('bytesIn', 0)
            bytes_out = network.get('bytesOut', 0)
            num_requests = network.get('numRequests', 0)
            
            # Converte bytes para MB
            bytes_in_mb = bytes_in / 1024 / 1024
            bytes_out_mb = bytes_out / 1024 / 1024
            
            performance_metrics = {
                "operations": {
                    "total": total_ops,
                    "insert": operations.get('insert', 0),
                    "query": operations.get('query', 0),
                    "update": operations.get('update', 0),
                    "delete": operations.get('delete', 0),
                    "getmore": operations.get('getmore', 0),
                    "command": operations.get('command', 0)
                },
                "network": {
                    "bytes_in": bytes_in,
                    "bytes_in_mb": round(bytes_in_mb, 2),
                    "bytes_out": bytes_out,
                    "bytes_out_mb": round(bytes_out_mb, 2),
                    "num_requests": num_requests,
                    "avg_request_size_mb": round(bytes_in_mb / num_requests, 4) if num_requests > 0 else 0
                },
                "uptime_hours": round(server_status.uptime / 3600, 2),
                "operations_per_hour": round(total_ops / (server_status.uptime / 3600), 2) if server_status.uptime > 0 else 0
            }
            
            self.logger.info("Métricas de performance obtidas com sucesso", 
                           total_operations=total_ops)
            return performance_metrics
            
        except Exception as e:
            self.logger.error("Erro ao obter métricas de performance", error=str(e))
            raise
    
    async def get_detailed_server_info(self) -> Dict[str, Any]:
        """
        Retorna informações detalhadas do servidor.
        
        Returns:
            Dicionário com informações detalhadas do servidor
            
        Raises:
            MongoDBConnectionError: Se não conseguir conectar ao MongoDB
        """
        try:
            self.logger.info("Obtendo informações detalhadas do servidor")
            
            # Obtém todas as informações
            server_status = await self.get_server_status()
            system_stats = await self.get_system_stats()
            health_info = await self.get_server_health()
            performance_metrics = await self.get_performance_metrics()
            
            detailed_info = {
                "server_status": server_status.model_dump(),
                "system_stats": system_stats,
                "health_info": health_info,
                "performance_metrics": performance_metrics,
                "summary": {
                    "version": server_status.version,
                    "uptime_days": round(server_status.uptime / 86400, 2),
                    "databases_count": system_stats.get('databases_count', 0),
                    "total_collections": system_stats.get('total_collections', 0),
                    "total_objects": system_stats.get('total_objects', 0),
                    "total_size_gb": round(system_stats.get('total_size', 0) / 1024 / 1024 / 1024, 2),
                    "status": health_info.get('status', 'unknown')
                }
            }
            
            self.logger.info("Informações detalhadas do servidor obtidas com sucesso")
            return detailed_info
            
        except Exception as e:
            self.logger.error("Erro ao obter informações detalhadas do servidor", error=str(e))
            raise 