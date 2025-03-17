"""
Weather MCP Server Implementation
"""
from typing import Dict, Optional, Any
import json
import re
from mcp_server import MCPServer, MCPRequest, MCPResponse, ContextScope
from weather_context import WeatherContext

class WeatherMCPServer(MCPServer):
    def __init__(self, api_key: str):
        super().__init__("weather")
        self.weather_context = WeatherContext(api_key)
        
    def _handle_query(self, request: MCPRequest) -> MCPResponse:
        """Handle weather-specific query requests"""
        try:
            # First check if we have cached weather data
            cached_data = self.retrieve_context(request.key, request.scope)
            if cached_data:
                return MCPResponse(
                    status="success",
                    data=cached_data,
                    metadata={
                        "server_id": self.server_id,
                        "scope": request.scope,
                        "key": request.key,
                        "source": "cache"
                    }
                )
            
            # If no cached data, fetch fresh weather data
            weather_text = self.weather_context.generate_weather_context(request.key)
            
            # Check for error messages in the weather text
            error_indicators = [
                "not found",
                "error",
                "invalid",
                "check the spelling",
                "tips for better results"
            ]
            
            if not weather_text or any(indicator in weather_text.lower() for indicator in error_indicators):
                return MCPResponse(
                    status="error",
                    data={
                        "message": weather_text or f"Could not fetch weather data for {request.key}",
                        "error_type": "location_not_found"
                    },
                    metadata={"server_id": self.server_id}
                )
                
            # Parse the weather text into structured data
            weather_data = self._parse_weather_text(weather_text)
            
            # Validate the parsed data
            if not self._is_valid_weather_data(weather_data):
                return MCPResponse(
                    status="error",
                    data={
                        "message": "Failed to parse weather data",
                        "error_type": "parsing_error",
                        "raw_text": weather_text
                    },
                    metadata={"server_id": self.server_id}
                )
            
            # Cache the weather data for future use
            self.store_context(request.key, weather_data, request.scope)
            
            return MCPResponse(
                status="success",
                data=weather_data,
                metadata={
                    "server_id": self.server_id,
                    "scope": request.scope,
                    "key": request.key,
                    "source": "api"
                }
            )
                
        except Exception as e:
            return MCPResponse(
                status="error",
                data={
                    "message": str(e),
                    "error_type": "system_error"
                },
                metadata={"server_id": self.server_id}
            )
            
    def _parse_weather_text(self, weather_text: str) -> Dict[str, Any]:
        """Parse weather text into structured data"""
        try:
            # Extract temperature
            temp_match = re.search(r"temperature is ([-\d.]+)°C", weather_text)
            temperature = float(temp_match.group(1)) if temp_match else None
            
            # Extract feels like
            feels_match = re.search(r"feels like ([-\d.]+)°C", weather_text)
            feels_like = float(feels_match.group(1)) if feels_match else None
            
            # Extract humidity
            humidity_match = re.search(r"humidity is (\d+)%", weather_text)
            humidity = int(humidity_match.group(1)) if humidity_match else None
            
            # Extract description
            desc_match = re.search(r"with (.+?)\.", weather_text)
            description = desc_match.group(1) if desc_match else None
            
            # Extract wind speed
            wind_match = re.search(r"wind speed is ([\d.]+) meters/sec", weather_text)
            wind_speed = float(wind_match.group(1)) if wind_match else None
            
            return {
                "temperature": temperature,
                "feels_like": feels_like,
                "humidity": humidity,
                "description": description,
                "wind_speed": wind_speed,
                "raw_text": weather_text
            }
            
        except Exception as e:
            # If parsing fails, return the raw text
            return {
                "temperature": None,
                "feels_like": None,
                "humidity": None,
                "description": None,
                "wind_speed": None,
                "raw_text": weather_text
            }
            
    def _is_valid_weather_data(self, weather_data: Dict[str, Any]) -> bool:
        """Check if the parsed weather data is valid"""
        required_fields = ["temperature", "humidity", "description"]
        return all(
            weather_data.get(field) is not None
            for field in required_fields
        )
            
    def _handle_store(self, request: MCPRequest) -> MCPResponse:
        """Handle weather-specific store requests"""
        try:
            if not isinstance(request.value, dict):
                return MCPResponse(
                    status="error",
                    data={
                        "message": "Weather data must be a dictionary",
                        "error_type": "invalid_format"
                    },
                    metadata={"server_id": self.server_id}
                )
                
            # Validate weather data format
            if not self._is_valid_weather_data(request.value):
                return MCPResponse(
                    status="error",
                    data={
                        "message": "Invalid weather data format",
                        "error_type": "validation_error",
                        "required_fields": ["temperature", "humidity", "description"]
                    },
                    metadata={"server_id": self.server_id}
                )
                
            return super()._handle_store(request)
            
        except Exception as e:
            return MCPResponse(
                status="error",
                data={
                    "message": str(e),
                    "error_type": "system_error"
                },
                metadata={"server_id": self.server_id}
            ) 