"""
Model Context Protocol (MCP) Server Implementation
"""
from typing import Dict, Optional, Any, List
import json
import time
from dataclasses import dataclass
from enum import Enum

class ContextScope(Enum):
    SESSION = "session"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"

@dataclass
class MCPRequest:
    action: str
    key: str
    value: Optional[Any] = None
    scope: str = "session"
    metadata: Dict = None

@dataclass
class MCPResponse:
    status: str
    data: Any
    metadata: Dict = None

class MCPServer:
    def __init__(self, server_id: str):
        self.server_id = server_id
        self.memory: Dict[str, Dict] = {
            ContextScope.SESSION.value: {},
            ContextScope.SHORT_TERM.value: {},
            ContextScope.LONG_TERM.value: {}
        }
        self.ttl: Dict[str, Dict] = {
            ContextScope.SESSION.value: 3600,  # 1 hour
            ContextScope.SHORT_TERM.value: 86400,  # 24 hours
            ContextScope.LONG_TERM.value: None  # No expiry
        }
    
    def store_context(self, key: str, value: Any, scope: str = ContextScope.SESSION.value) -> None:
        """Store context with specified scope and TTL"""
        if scope not in self.memory:
            raise ValueError(f"Invalid scope: {scope}")
            
        self.memory[scope][key] = {
            "value": value,
            "timestamp": time.time()
        }
    
    def retrieve_context(self, key: str, scope: str = ContextScope.SESSION.value) -> Optional[Any]:
        """Retrieve context from memory with TTL check"""
        if scope not in self.memory:
            return None
            
        context_data = self.memory[scope].get(key)
        if not context_data:
            return None
            
        # Check TTL
        ttl = self.ttl[scope]
        if ttl is not None:
            age = time.time() - context_data["timestamp"]
            if age > ttl:
                del self.memory[scope][key]
                return None
                
        return context_data["value"]
    
    def handle_request(self, request: MCPRequest) -> MCPResponse:
        """Handle incoming MCP requests"""
        try:
            if request.action == "query":
                return self._handle_query(request)
            elif request.action == "store":
                return self._handle_store(request)
            elif request.action == "delete":
                return self._handle_delete(request)
            elif request.action == "list":
                return self._handle_list(request)
            else:
                return MCPResponse(
                    status="error",
                    data={"message": f"Invalid action: {request.action}"},
                    metadata={"server_id": self.server_id}
                )
        except Exception as e:
            return MCPResponse(
                status="error",
                data={"message": str(e)},
                metadata={"server_id": self.server_id}
            )
    
    def _handle_query(self, request: MCPRequest) -> MCPResponse:
        """Handle query requests"""
        value = self.retrieve_context(request.key, request.scope)
        return MCPResponse(
            status="success" if value is not None else "not_found",
            data=value,
            metadata={
                "server_id": self.server_id,
                "scope": request.scope,
                "key": request.key
            }
        )
    
    def _handle_store(self, request: MCPRequest) -> MCPResponse:
        """Handle store requests"""
        if request.value is None:
            return MCPResponse(
                status="error",
                data={"message": "No value provided for storage"},
                metadata={"server_id": self.server_id}
            )
            
        self.store_context(request.key, request.value, request.scope)
        return MCPResponse(
            status="success",
            data={"message": "Context stored successfully"},
            metadata={
                "server_id": self.server_id,
                "scope": request.scope,
                "key": request.key
            }
        )
    
    def _handle_delete(self, request: MCPRequest) -> MCPResponse:
        """Handle delete requests"""
        if request.scope in self.memory and request.key in self.memory[request.scope]:
            del self.memory[request.scope][request.key]
            return MCPResponse(
                status="success",
                data={"message": "Context deleted successfully"},
                metadata={
                    "server_id": self.server_id,
                    "scope": request.scope,
                    "key": request.key
                }
            )
        return MCPResponse(
            status="not_found",
            data={"message": "Context not found"},
            metadata={
                "server_id": self.server_id,
                "scope": request.scope,
                "key": request.key
            }
        )
    
    def _handle_list(self, request: MCPRequest) -> MCPResponse:
        """Handle list requests"""
        if request.scope in self.memory:
            keys = list(self.memory[request.scope].keys())
            return MCPResponse(
                status="success",
                data={"keys": keys},
                metadata={
                    "server_id": self.server_id,
                    "scope": request.scope
                }
            )
        return MCPResponse(
            status="error",
            data={"message": f"Invalid scope: {request.scope}"},
            metadata={"server_id": self.server_id}
        ) 