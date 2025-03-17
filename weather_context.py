import requests
from typing import Dict, Optional
import json
from datetime import datetime

class WeatherContext:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
    def get_weather_by_city(self, city: str) -> Optional[Dict]:
        """
        Fetch weather data for a given city
        """
        try:
            # Get current weather
            weather_url = f"{self.base_url}/weather"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"  # Use metric units
            }
            
            response = requests.get(weather_url, params=params)
            
            if response.status_code == 401:
                print("\nError: OpenWeather API key is invalid or not yet activated.")
                print("Note: New API keys take about 2 hours to activate.")
                print("Please check your API key at: https://home.openweathermap.org/api_keys")
                return None
            elif response.status_code == 404:
                print(f"\nError: City '{city}' not found.")
                return None
                
            response.raise_for_status()
            weather_data = response.json()
            
            # Format the weather data into a readable context
            formatted_data = {
                "temperature": round(weather_data["main"]["temp"], 1),
                "feels_like": round(weather_data["main"]["feels_like"], 1),
                "humidity": weather_data["main"]["humidity"],
                "description": weather_data["weather"][0]["description"],
                "wind_speed": weather_data["wind"]["speed"],
                "timestamp": datetime.utcfromtimestamp(weather_data["dt"]).strftime('%Y-%m-%d %H:%M:%S UTC')
            }
            
            return formatted_data
            
        except requests.exceptions.RequestException as e:
            print(f"\nError connecting to weather service: {str(e)}")
            return None
        except (KeyError, ValueError) as e:
            print(f"\nError parsing weather data: {str(e)}")
            return None
            
    def generate_weather_context(self, city: str) -> str:
        """
        Generate a natural language context string from weather data
        """
        weather_data = self.get_weather_by_city(city)
        if not weather_data:
            return "I apologize, but I couldn't fetch the current weather data. However, I'll try to help with your query based on my general knowledge."
            
        context = (
            f"Current weather in {city} as of {weather_data['timestamp']}: "
            f"The temperature is {weather_data['temperature']}°C "
            f"(feels like {weather_data['feels_like']}°C) with {weather_data['description']}. "
            f"The humidity is {weather_data['humidity']}% and "
            f"wind speed is {weather_data['wind_speed']} meters/sec."
        )
        
        return context 