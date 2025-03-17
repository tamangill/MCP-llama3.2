# Model Context Protocol (MCP) Implementation

This project implements the Model Context Protocol (MCP) for managing context in AI applications. The implementation includes a base MCP server, client, and a specialized weather context server.

## Features

- **Base MCP Server**
  - Context storage with different scopes (session, short-term, long-term)
  - TTL-based context expiration
  - CRUD operations for context management
  - Error handling and validation

- **MCP Client**
  - Server registration and management
  - Simplified interface for context operations
  - Multi-server support

- **Weather MCP Server**
  - Weather data fetching and caching
  - Structured data parsing
  - Error handling for invalid locations
  - Data validation

## Components

### MCP Server (`mcp_server.py`)

The base MCP server implementation provides:

```python
class MCPServer:
    def __init__(self, server_id: str)
    def store_context(self, key: str, value: Any, scope: str)
    def retrieve_context(self, key: str, scope: str)
    def handle_request(self, request: MCPRequest)
```

### MCP Client (`mcp_client.py`)

The client interface for interacting with MCP servers:

```python
class MCPClient:
    def __init__(self)
    def register_server(self, server_id: str, server: Any)
    def query_context(self, server_id: str, key: str, scope: str)
    def store_context(self, server_id: str, key: str, value: Any, scope: str)
```

### Weather MCP Server (`weather_mcp_server.py`)

A specialized server for weather data:

```python
class WeatherMCPServer(MCPServer):
    def __init__(self, api_key: str)
    def _handle_query(self, request: MCPRequest)
    def _parse_weather_text(self, weather_text: str)
```

## Usage

1. Initialize the MCP client:
```python
from mcp_client import MCPClient
client = MCPClient()
```

2. Create and register an MCP server:
```python
from weather_mcp_server import WeatherMCPServer
weather_server = WeatherMCPServer(api_key)
client.register_server("weather", weather_server)
```

3. Query weather data:
```python
weather_data = client.query_context("weather", "Seattle")
if weather_data:
    print(f"Temperature: {weather_data['temperature']}°C")
    print(f"Humidity: {weather_data['humidity']}%")
    print(f"Description: {weather_data['description']}")
```

## Testing

Run the test suite:
```bash
python3 test_mcp.py -v
```

The test suite includes:
- Basic MCP server operations
- Client functionality
- Weather server specific tests
- Error handling cases

## Error Handling

The implementation includes comprehensive error handling:

1. Invalid locations:
```python
{
    "status": "error",
    "data": {
        "message": "Location not found",
        "error_type": "location_not_found"
    }
}
```

2. Data validation:
```python
{
    "status": "error",
    "data": {
        "message": "Invalid weather data format",
        "error_type": "validation_error",
        "required_fields": ["temperature", "humidity", "description"]
    }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite
5. Submit a pull request

## License

MIT License 