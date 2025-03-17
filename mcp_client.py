"""
Model Context Protocol (MCP) Client Implementation
"""
from typing import Dict, Optional, Any, List
import json
from dataclasses import asdict
from mcp_server import MCPRequest, MCPResponse, ContextScope

class MCPClient:
    def __init__(self):
        self.servers: Dict[str, Any] = {}
        
    def register_server(self, server_id: str, server: Any) -> None:
        """Register an MCP server with this client"""
        self.servers[server_id] = server
        
    def query_context(self, server_id: str, key: str, scope: str = ContextScope.SESSION.value) -> Optional[Any]:
        """Query context from a specific server"""
        if server_id not in self.servers:
            raise ValueError(f"Server not found: {server_id}")
            
        request = MCPRequest(
            action="query",
            key=key,
            scope=scope
        )
        
        response = self.servers[server_id].handle_request(request)
        return response.data if response.status == "success" else None
        
    def store_context(self, server_id: str, key: str, value: Any, scope: str = ContextScope.SESSION.value) -> bool:
        """Store context on a specific server"""
        if server_id not in self.servers:
            raise ValueError(f"Server not found: {server_id}")
            
        request = MCPRequest(
            action="store",
            key=key,
            value=value,
            scope=scope
        )
        
        response = self.servers[server_id].handle_request(request)
        return response.status == "success"
        
    def delete_context(self, server_id: str, key: str, scope: str = ContextScope.SESSION.value) -> bool:
        """Delete context from a specific server"""
        if server_id not in self.servers:
            raise ValueError(f"Server not found: {server_id}")
            
        request = MCPRequest(
            action="delete",
            key=key,
            scope=scope
        )
        
        response = self.servers[server_id].handle_request(request)
        return response.status == "success"
        
    def list_context(self, server_id: str, scope: str = ContextScope.SESSION.value) -> List[str]:
        """List all context keys from a specific server"""
        if server_id not in self.servers:
            raise ValueError(f"Server not found: {server_id}")
            
        request = MCPRequest(
            action="list",
            key="*",  # Wildcard for listing all keys
            scope=scope
        )
        
        response = self.servers[server_id].handle_request(request)
        return response.data.get("keys", []) if response.status == "success" else [] 