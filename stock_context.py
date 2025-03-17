import requests
from typing import Dict, Optional
import json
from datetime import datetime

class StockContext:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        
    def get_stock_quote(self, symbol: str) -> Optional[Dict]:
        """
        Fetch real-time stock quote for a given symbol
        """
        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Check for rate limit message
            if "Information" in data and "API rate limit" in data["Information"]:
                print("\nError: Alpha Vantage API rate limit reached (25 requests per day on free tier)")
                print("To increase the limit, get a premium API key at: https://www.alphavantage.co/premium/")
                return None
            
            # Check if we got valid data
            if "Global Quote" not in data or not data["Global Quote"]:
                print(f"\nError: No data found for symbol '{symbol}'")
                return None
                
            quote = data["Global Quote"]
            
            # Format the stock data
            formatted_data = {
                "symbol": quote["01. symbol"],
                "price": float(quote["05. price"]),
                "change": float(quote["09. change"]),
                "change_percent": quote["10. change percent"].rstrip('%'),
                "volume": int(quote["06. volume"]),
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return formatted_data
            
        except requests.exceptions.RequestException as e:
            print(f"\nError connecting to stock service: {str(e)}")
            return None
        except (KeyError, ValueError) as e:
            print(f"\nError parsing stock data: {str(e)}")
            return None
            
    def generate_stock_context(self, symbol: str) -> str:
        """
        Generate a natural language context string from stock data
        """
        stock_data = self.get_stock_quote(symbol.upper())
        if not stock_data:
            return ("I apologize, but I couldn't fetch the current stock data due to API rate limits. "
                   "The free tier of Alpha Vantage allows 25 requests per day. "
                   "I'll try to help with your query based on my general knowledge.")
            
        # Format the price with 2 decimal places
        price = f"${stock_data['price']:.2f}"
        change = f"${abs(stock_data['change']):.2f}"
        direction = "up" if stock_data['change'] >= 0 else "down"
        
        context = (
            f"Current stock data for {stock_data['symbol']} as of {stock_data['timestamp']}: "
            f"The stock is trading at {price}, {direction} {change} ({stock_data['change_percent']}%) "
            f"with a volume of {stock_data['volume']:,} shares."
        )
        
        return context 