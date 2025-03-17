import requests
from typing import Dict, Optional, Tuple
import json
from datetime import datetime

class WeatherContext:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.geocoding_url = "http://api.openweathermap.org/geo/1.0/direct"
        
    def get_coordinates(self, location: str) -> Optional[Tuple[float, float]]:
        """
        Convert location to coordinates using OpenWeather's Geocoding API.
        
        Supported location formats:
        1. City name: "London"
        2. City, State: "Los Angeles, California" or "Los Angeles, CA"
        3. City, Country: "London, UK" or "London, GB"
        4. City, State, Country: "Los Angeles, CA, US"
        
        Note:
        - State codes should be in ISO 3166-2 format (e.g., "CA" for California)
        - Country codes should be in ISO 3166 format (e.g., "US", "GB", "IN")
        - For cities in the USA, it's recommended to include the state to avoid ambiguity
        """
        try:
            # Clean up the location string
            location = location.strip()
            
            # Split into components (city, state, country)
            parts = [part.strip() for part in location.split(',')]
            
            # Build the query string based on the number of components
            if len(parts) == 1:
                # Just city name
                q = parts[0]
            elif len(parts) == 2:
                # City and State/Country
                state_or_country = parts[1].strip().upper()
                # If it's a US state abbreviation, add US as country
                if len(state_or_country) == 2 and state_or_country.isalpha():
                    q = f"{parts[0]},{state_or_country},US"
                else:
                    q = f"{parts[0]},{state_or_country}"
            elif len(parts) == 3:
                # City, State, and Country
                q = f"{parts[0]},{parts[1]},{parts[2]}"
            else:
                print("\nError: Invalid location format. Please use one of the following formats:")
                print("- City name: 'London'")
                print("- City, State: 'Los Angeles, California' or 'Los Angeles, CA'")
                print("- City, Country: 'London, UK' or 'London, GB'")
                print("- City, State, Country: 'Los Angeles, CA, US'")
                return None
            
            params = {
                "q": q,
                "limit": 1,  # Get only the first (most relevant) result
                "appid": self.api_key
            }
            
            response = requests.get(self.geocoding_url, params=params)
            
            if response.status_code == 401:
                print("\nError: OpenWeather API key is invalid or not yet activated.")
                print("Note: New API keys take about 2 hours to activate.")
                print("Please check your API key at: https://home.openweathermap.org/api_keys")
                return None
                
            response.raise_for_status()
            locations = response.json()
            
            if not locations:
                print(f"\nError: Location '{location}' not found.")
                print("\nTips for better results:")
                print("1. Check the spelling of the city name")
                print("2. For US cities, include the state code (e.g., 'New York, NY')")
                print("3. For international cities, include the country code (e.g., 'Paris, FR')")
                print("4. Use official city names (e.g., 'Saint Petersburg' instead of 'St. Petersburg')")
                return None
                
            # Get the first (most relevant) result
            location_data = locations[0]
            
            # Print additional information about the found location
            print(f"\nFound location: {location_data.get('name', '')}, ", end='')
            if state := location_data.get('state'):
                print(f"{state}, ", end='')
            print(f"{location_data.get('country', '')}")
            
            return (location_data['lat'], location_data['lon'])
            
        except requests.exceptions.RequestException as e:
            print(f"\nError connecting to geocoding service: {str(e)}")
            return None
        except (KeyError, ValueError, IndexError) as e:
            print(f"\nError parsing geocoding data: {str(e)}")
            return None
    
    def get_weather_by_coordinates(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Fetch weather data for given coordinates
        """
        try:
            weather_url = f"{self.base_url}/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"  # Use metric units
            }
            
            response = requests.get(weather_url, params=params)
            response.raise_for_status()
            weather_data = response.json()
            
            # Format the weather data into a readable context
            formatted_data = {
                "city": weather_data["name"],
                "country": weather_data["sys"]["country"],
                "temperature": round(weather_data["main"]["temp"], 1),
                "feels_like": round(weather_data["main"]["feels_like"], 1),
                "humidity": weather_data["main"]["humidity"],
                "description": weather_data["weather"][0]["description"],
                "wind_speed": weather_data["wind"]["speed"],
                "coordinates": {"lat": lat, "lon": lon},
                "timestamp": datetime.utcfromtimestamp(weather_data["dt"]).strftime('%Y-%m-%d %H:%M:%S UTC')
            }
            
            return formatted_data
            
        except requests.exceptions.RequestException as e:
            print(f"\nError connecting to weather service: {str(e)}")
            return None
        except (KeyError, ValueError) as e:
            print(f"\nError parsing weather data: {str(e)}")
            return None
            
    def get_weather_by_city(self, city: str) -> Optional[Dict]:
        """
        Fetch weather data for a given city using geocoding
        """
        coordinates = self.get_coordinates(city)
        if not coordinates:
            return None
            
        lat, lon = coordinates
        return self.get_weather_by_coordinates(lat, lon)
            
    def generate_weather_context(self, city: str) -> str:
        """
        Generate a natural language context string from weather data
        """
        weather_data = self.get_weather_by_city(city)
        if not weather_data:
            return "I apologize, but I couldn't fetch the current weather data. However, I'll try to help with your query based on my general knowledge."
            
        context = (
            f"Current weather in {weather_data['city']}, {weather_data['country']} "
            f"(coordinates: {weather_data['coordinates']['lat']:.2f}°N, {weather_data['coordinates']['lon']:.2f}°E) "
            f"as of {weather_data['timestamp']}: "
            f"The temperature is {weather_data['temperature']}°C "
            f"(feels like {weather_data['feels_like']}°C) with {weather_data['description']}. "
            f"The humidity is {weather_data['humidity']}% and "
            f"wind speed is {weather_data['wind_speed']} meters/sec."
        )
        
        return context 