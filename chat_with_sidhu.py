import requests
import json
import sys
import os
import re
from weather_context import WeatherContext
from stock_context import StockContext
from typing import Optional
from personalities.sidhu_moosewala import PERSONALITY, PROMPT_TEMPLATE, WELCOME_MESSAGE

def load_config():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            return config
    except FileNotFoundError:
        print("Error: config.json file not found!")
        return {}
    except json.JSONDecodeError:
        print("Error: config.json is not valid JSON!")
        return {}

# Initialize contexts
config = load_config()
weather_context = WeatherContext(config.get('openweather_api_key', ''))
stock_context = StockContext(config.get('alphavantage_api_key', ''))

def extract_city_from_query(query: str) -> str:
    """
    Extract city name from weather-related queries
    """
    # Common patterns for weather queries, including Punjabi style
    patterns = [
        r"weather (?:is |in |at |for )?([A-Za-z\s,]+?)(?:\?)?$",
        r"what'?s? (?:the )?weather (?:like )?(?:in |at |for )?([A-Za-z\s,]+?)(?:\?)?$",
        r"how'?s? (?:the )?weather (?:in |at |for )?([A-Za-z\s,]+?)(?:\?)?$",
        r"temperature (?:is |in |at |for )?([A-Za-z\s,]+?)(?:\?)?$",
        r"what'?s? (?:the )?temperature (?:like )?(?:in |at |for )?([A-Za-z\s,]+?)(?:\?)?$",
        r"how'?s? (?:the )?temperature (?:in |at |for )?([A-Za-z\s,]+?)(?:\?)?$",
        r"(?:what's|whats|hows|how's) (?:it (?:like )?)?(?:in |at )?([A-Za-z\s,]+?)(?:\?)?$",
        r"(?:pind|shehar) (?:ch |de |ton )?([A-Za-z\s,]+?)(?:\?)?$",  # Punjabi style queries
        r"([A-Za-z\s,]+?) (?:da |ch |de )?(?:weather|mausam)(?:\?)?$"  # More Punjabi style
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query.lower())
        if match:
            city = match.group(1).strip()
            city = ' '.join(city.split())
            parts = city.split(',')
            formatted_parts = []
            for part in parts:
                formatted_parts.append(' '.join(word.capitalize() for word in part.strip().split()))
            city = ','.join(formatted_parts)
            return city
    return ""

def extract_stock_symbol(query: str) -> str:
    """
    Extract stock symbol from stock-related queries
    """
    patterns = [
        r"(?:stock|share|dollar) (?:price )?(?:for |of |de )?([A-Za-z]+)(?:\?)?$",
        r"how (?:much|is) (?:is |does )?([A-Za-z]+) (?:stock |share )?(?:cost|trading at|worth)(?:\?)?$",
        r"what'?s? (?:the )?(?:stock |share )?(?:price |value )?(?:of |for )?([A-Za-z]+)(?:\?)?$",
        r"^([A-Za-z]+) (?:stock |share |de bhaa|shares kiddan)(?:price|value)?(?:\?)?$"
    ]
    
    query = query.lower()
    for pattern in patterns:
        match = re.search(pattern, query)
        if match:
            symbol = match.group(1).strip()
            if symbol in ['stock', 'share', 'price', 'value']:
                continue
            return symbol
    return ""

def chat_with_model(prompt: str, context: Optional[str] = None) -> str:
    """
    Send prompts to Ollama API to get responses in Sidhu Moosewala style
    """
    system_prompt = PROMPT_TEMPLATE.format(
        personality=PERSONALITY,
        context=context if context else 'No additional context provided'
    )
    
    try:
        response = requests.post('http://localhost:11434/api/generate',
                               json={
                                   "model": "llama3.2:latest",
                                   "prompt": f"{system_prompt}\n\nQuestion: {prompt}",
                                   "stream": False
                               })
        response.raise_for_status()
        return response.json()['response']
    except requests.exceptions.RequestException as e:
        print(f"Error connecting with server paaji: {e}")
        return None
    except KeyError as e:
        print(f"Server ne galti kiti paaji: {e}")
        return None

def main():
    if not config.get('alphavantage_api_key') or config['alphavantage_api_key'] == "YOUR_ALPHA_VANTAGE_API_KEY":
        print("Sunno paaji: Stock data waste API key di lor aa")
        print("1. https://www.alphavantage.co/support/#api-key te jao")
        print("2. Free API key lao")
        print("3. Config.json ch add karo")
        print("\n")
    
    print(WELCOME_MESSAGE)
    
    while True:
        try:
            # Get user input
            user_input = input("\nTusi: ")
            
            if not user_input.strip():
                continue
            
            # Check if it's a weather-related query
            city = extract_city_from_query(user_input)
            context = ""
            
            if city:
                print("\nPind da mausam check kar reha haan...")
                context = weather_context.generate_weather_context(city)
            else:
                # Check if it's a stock-related query
                symbol = extract_stock_symbol(user_input)
                if symbol:
                    print("\nDollar de bhaa check kar reha haan...")
                    context = stock_context.generate_stock_context(symbol)
            
            # Get response from model
            print("\nSoch reha haan paaji...")
            response = chat_with_model(user_input, context=context)
            
            if response:
                print("\nSidhu: ", response)
            else:
                print("\nMaafi paaji, koi gadbad ho gayi")
                
        except KeyboardInterrupt:
            print("\n\nChanga phir milange! Dil Da Ni Mada 🙏")
            sys.exit(0)
        except Exception as e:
            print(f"\nO paaji, koi error aa gya: {e}")

if __name__ == "__main__":
    main() 