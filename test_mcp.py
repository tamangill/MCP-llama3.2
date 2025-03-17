"""
Test suite for MCP implementation
"""
import unittest
import json
from mcp_server import MCPServer, MCPRequest, MCPResponse, ContextScope
from mcp_client import MCPClient
from weather_mcp_server import WeatherMCPServer

class TestMCPServer(unittest.TestCase):
    def setUp(self):
        self.server = MCPServer("test_server")
        
    def test_store_and_retrieve(self):
        """Test basic store and retrieve operations"""
        # Store data
        request = MCPRequest(
            action="store",
            key="test_key",
            value={"data": "test_value"},
            scope=ContextScope.SESSION.value
        )
        response = self.server.handle_request(request)
        self.assertEqual(response.status, "success")
        
        # Retrieve data
        request = MCPRequest(
            action="query",
            key="test_key",
            scope=ContextScope.SESSION.value
        )
        response = self.server.handle_request(request)
        self.assertEqual(response.status, "success")
        self.assertEqual(response.data["data"], "test_value")
        
    def test_delete(self):
        """Test delete operation"""
        # Store data
        request = MCPRequest(
            action="store",
            key="test_key",
            value={"data": "test_value"},
            scope=ContextScope.SESSION.value
        )
        self.server.handle_request(request)
        
        # Delete data
        request = MCPRequest(
            action="delete",
            key="test_key",
            scope=ContextScope.SESSION.value
        )
        response = self.server.handle_request(request)
        self.assertEqual(response.status, "success")
        
        # Verify deletion
        request = MCPRequest(
            action="query",
            key="test_key",
            scope=ContextScope.SESSION.value
        )
        response = self.server.handle_request(request)
        self.assertEqual(response.status, "not_found")

class TestMCPClient(unittest.TestCase):
    def setUp(self):
        self.client = MCPClient()
        self.server = MCPServer("test_server")
        self.client.register_server("test_server", self.server)
        
    def test_server_registration(self):
        """Test server registration"""
        self.assertIn("test_server", self.client.servers)
        
    def test_context_operations(self):
        """Test context operations through client"""
        # Store context
        success = self.client.store_context(
            "test_server",
            "test_key",
            {"data": "test_value"}
        )
        self.assertTrue(success)
        
        # Query context
        data = self.client.query_context("test_server", "test_key")
        self.assertEqual(data["data"], "test_value")
        
        # Delete context
        success = self.client.delete_context("test_server", "test_key")
        self.assertTrue(success)
        
        # Verify deletion
        data = self.client.query_context("test_server", "test_key")
        self.assertIsNone(data)

class TestWeatherMCPServer(unittest.TestCase):
    def setUp(self):
        with open("config.json") as f:
            config = json.load(f)
        self.server = WeatherMCPServer(config["openweather_api_key"])
        
    def test_weather_query(self):
        """Test weather query functionality"""
        request = MCPRequest(
            action="query",
            key="Seattle",
            scope=ContextScope.SESSION.value
        )
        response = self.server.handle_request(request)
        
        self.assertEqual(response.status, "success")
        self.assertIn("temperature", response.data)
        self.assertIn("humidity", response.data)
        self.assertIn("description", response.data)
        
    def test_invalid_city(self):
        """Test query with invalid city"""
        request = MCPRequest(
            action="query",
            key="NonexistentCity123",
            scope=ContextScope.SESSION.value
        )
        response = self.server.handle_request(request)
        
        self.assertEqual(response.status, "error")
        
    def test_weather_caching(self):
        """Test weather data caching"""
        # First query
        request = MCPRequest(
            action="query",
            key="Seattle",
            scope=ContextScope.SESSION.value
        )
        response1 = self.server.handle_request(request)
        
        # Second query (should be from cache)
        response2 = self.server.handle_request(request)
        
        self.assertEqual(response1.data, response2.data)
        self.assertEqual(response2.metadata["source"], "cache")

if __name__ == "__main__":
    unittest.main() 