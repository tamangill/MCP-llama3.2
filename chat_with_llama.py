import requests
import json
import sys
import os
import re
from weather_context import WeatherContext
from stock_context import StockContext

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
    # Common patterns for weather queries
    patterns = [
        r"weather (?:is |in |at |for )([A-Za-z\s,]+?)(?:\?)?$",
        r"what'?s? (?:the )?weather (?:like )?(?:in |at |for )([A-Za-z\s,]+?)(?:\?)?$",
        r"how'?s? (?:the )?weather (?:in |at |for )([A-Za-z\s,]+?)(?:\?)?$"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query.lower())
        if match:
            # Clean up the city name
            city = match.group(1).strip()
            # Replace multiple spaces with single space
            city = ' '.join(city.split())
            # Properly capitalize city names
            city = ' '.join(word.capitalize() for word in city.split())
            return city
    return ""

def extract_stock_symbol(query: str) -> str:
    """
    Extract stock symbol from stock-related queries
    """
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

def chat_with_model(prompt, model="llama3.2:latest", context=""):
    """
    Send a prompt to the Ollama API and get the response
    """
    try:
        # Construct a more explicit prompt that tells the model to use the context
        if context:
            full_prompt = (
                "You are a helpful assistant with access to real-time data. "
                f"Here is the current, real-time information: {context}\n\n"
                f"Question: {prompt}\n\n"
                "Important: This is real, current data that you should use in your response. "
                "Do not say you don't have access to real-time data, as this data has just been provided to you. "
                "Please provide a natural, conversational response that incorporates this current information."
            )
        else:
            full_prompt = prompt
        
        response = requests.post('http://localhost:11434/api/generate',
                               json={
                                   "model": model,
                                   "prompt": full_prompt,
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

def main():
    if not config.get('alphavantage_api_key') or config['alphavantage_api_key'] == "YOUR_ALPHA_VANTAGE_API_KEY":
        print("Note: To get stock data, please set up an Alpha Vantage API key in config.json")
        print("1. Go to https://www.alphavantage.co/support/#api-key")
        print("2. Get your free API key")
        print("3. Add it to config.json")
        print("\n")
    
    print("Welcome to LLaMA Chat! (Press Ctrl+C to exit)")
    print("-------------------------------------------")
    print("You can ask about:")
    print("- Weather: 'What's the weather like in London?'")
    print("- Stocks: 'What's the stock price of AAPL?'")
    print("-------------------------------------------\n")
    
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ")
            
            if not user_input.strip():
                continue
            
            # Check if it's a weather-related query
            city = extract_city_from_query(user_input)
            context = ""
            
            if city:
                print("\nFetching weather data...")
                context = weather_context.generate_weather_context(city)
            else:
                # Check if it's a stock-related query
                symbol = extract_stock_symbol(user_input)
                if symbol:
                    print("\nFetching stock data...")
                    context = stock_context.generate_stock_context(symbol)
            
            # Get response from model
            print("\nThinking...")
            response = chat_with_model(user_input, context=context)
            
            if response:
                print("\nLLaMA:", response)
            else:
                print("\nError: Failed to get response from the model")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main() 