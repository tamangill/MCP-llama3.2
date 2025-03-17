"""
Chat interface with MCP integration for context management
"""
import requests
import json
import sys
import os
import re
from typing import Dict, Optional
from mcp_client import MCPClient
from mcp_server import ContextScope
from weather_mcp_server import WeatherMCPServer
from weather_context import WeatherContext
from stock_context import StockContext
from personalities.surrey_jack import PERSONALITY, PROMPT_TEMPLATE, WELCOME_MESSAGE

class ChatInterface:
    def __init__(self, config_path: str = "config.json"):
        # Load configuration
        with open(config_path) as f:
            self.config = json.load(f)
            
        # Initialize MCP client
        self.mcp_client = MCPClient()
        
        # Initialize and register MCP servers
        self._init_weather_server()
        
        # Initialize stock context
        self.stock_context = StockContext(self.config.get('alphavantage_api_key', ''))
        
    def _init_weather_server(self):
        """Initialize and register the weather MCP server"""
        weather_server = WeatherMCPServer(self.config["openweather_api_key"])
        self.mcp_client.register_server("weather", weather_server)
        
    def chat_with_model(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Send prompts to Ollama API with MCP context management
        """
        try:
            # Extract city from prompt if it's a weather query
            if "weather" in prompt.lower():
                city = self._extract_city_from_query(prompt)
                if city:
                    # Query weather context from MCP server
                    weather_context = self.mcp_client.query_context("weather", city)
                    if weather_context:
                        context = f"Weather context: {json.dumps(weather_context)}\n{context or ''}"
            
            # Build system prompt with context
            system_prompt = self._build_system_prompt(context)
            
            # Call Ollama API with the system prompt and user prompt
            response = self._call_ollama_api(system_prompt, prompt)
            
            return response
            
        except Exception as e:
            return f"Error: {str(e)}"
            
    def _extract_city_from_query(self, query: str) -> Optional[str]:
        """Extract city name from query"""
        # Common patterns for weather queries
        patterns = [
            r"weather (?:is |in |at |for )?([A-Za-z\s,]+?)(?:\?)?$",
            r"what'?s? (?:the )?weather (?:like )?(?:in |at |for )?([A-Za-z\s,]+?)(?:\?)?$",
            r"how'?s? (?:the )?weather (?:in |at |for )?([A-Za-z\s,]+?)(?:\?)?$",
            r"temperature (?:is |in |at |for )?([A-Za-z\s,]+?)(?:\?)?$",
            r"what'?s? (?:the )?temperature (?:like )?(?:in |at |for )?([A-Za-z\s,]+?)(?:\?)?$",
            r"how'?s? (?:the )?temperature (?:in |at |for )?([A-Za-z\s,]+?)(?:\?)?$",
            r"(?:what's|whats|hows|how's) (?:it (?:like )?)?(?:in |at )?([A-Za-z\s,]+?)(?:\?)?$"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                # Clean up the city name
                city = match.group(1).strip()
                # Replace multiple spaces with single space
                city = ' '.join(city.split())
                # Keep commas for state/country codes
                # Properly capitalize each word except after a comma
                parts = city.split(',')
                formatted_parts = []
                for part in parts:
                    formatted_parts.append(' '.join(word.capitalize() for word in part.strip().split()))
                city = ','.join(formatted_parts)
                return city
        return None
        
    def _build_system_prompt(self, context: Optional[str]) -> str:
        """Build system prompt with context"""
        base_prompt = PROMPT_TEMPLATE.format(
            personality=PERSONALITY,
            context=context if context else 'No additional context provided'
        )
        return base_prompt
        
    def _call_ollama_api(self, system_prompt: str, user_prompt: str) -> str:
        """Call Ollama API with prompts"""
        try:
            response = requests.post('http://localhost:11434/api/generate',
                                   json={
                                       "model": "llama3.2:latest",
                                       "prompt": f"{system_prompt}\n\nQuestion: {user_prompt}",
                                       "stream": False
                                   })
            response.raise_for_status()
            return response.json()['response']
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with Ollama: {e}")
            return None
        except KeyError as e:
            print(f"Unexpected response format: {e}")
            return None

def extract_stock_symbol(query: str) -> str:
    """Extract stock symbol from stock-related queries"""
    patterns = [
        r"(?:stock|share) (?:price )?(?:for |of )?([A-Za-z]+)(?:\?)?$",
        r"how (?:much|is) (?:is |does )?([A-Za-z]+) (?:stock |share )?(?:cost|trading at|worth)(?:\?)?$",
        r"what'?s? (?:the )?(?:stock |share )?(?:price |value )?(?:of |for )?([A-Za-z]+)(?:\?)?$",
        r"^([A-Za-z]+) (?:stock |share )?(?:price|value)(?:\?)?$"
    ]
    
    query = query.lower()
    for pattern in patterns:
        match = re.search(pattern, query)
        if match:
            symbol = match.group(1).strip()
            # Ignore common words that might be matched
            if symbol in ['stock', 'share', 'price', 'value']:
                continue
            return symbol
    return ""

def main():
    chat = ChatInterface()
    
    if not chat.config.get('alphavantage_api_key') or chat.config['alphavantage_api_key'] == "YOUR_ALPHA_VANTAGE_API_KEY":
        print("Note: To get stock data, please set up an Alpha Vantage API key in config.json")
        print("1. Go to https://www.alphavantage.co/support/#api-key")
        print("2. Get your free API key")
        print("3. Add it to config.json")
        print("\n")
    
    print(WELCOME_MESSAGE)
    print("Chat interface initialized. Type 'exit' to quit.")
    
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ")
            
            if user_input.lower() == "exit":
                break
            
            if not user_input.strip():
                continue
            
            # Check if it's a weather-related query
            city = chat._extract_city_from_query(user_input)
            context = ""
            
            if city:
                print("\nChecking the weather tingz...")
                context = chat.mcp_client.query_context("weather", city)
                if context:
                    context = f"Weather context: {json.dumps(context)}\n{context}"
            else:
                # Check if it's a stock-related query
                symbol = extract_stock_symbol(user_input)
                if symbol:
                    print("\nPeepin them stocks fam...")
                    context = chat.stock_context.generate_stock_context(symbol)
            
            # Get response from model
            print("\nAyo lemme think bout that...")
            response = chat.chat_with_model(user_input, context=context)
            
            if response:
                print("\nYour boy:", response)
            else:
                print("\nMy bad fam, couldn't get that response styll")
                
        except KeyboardInterrupt:
            print("\n\nAight bet, I'm out! Stay blessed fam 🙏")
            sys.exit(0)
        except Exception as e:
            print(f"\nDamn, we caught an error fam: {e}")

if __name__ == "__main__":
    main() 