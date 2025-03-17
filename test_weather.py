import json
from weather_context import WeatherContext

def test_weather():
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
        
    # Initialize weather context
    weather = WeatherContext(config['openweather_api_key'])
    
    # Test cities
    test_cities = [
        'Seattle',
        'Seattle, WA',
        'Seattle, WA, US'
    ]
    
    print("Testing weather API for Seattle variations...")
    print("===========================================")
    
    for city in test_cities:
        print(f"\nTesting city: {city}")
        print("-" * 50)
        
        # Test coordinates
        coords = weather.get_coordinates(city)
        if coords:
            print(f"Coordinates found: {coords}")
            
            # Test weather data
            weather_data = weather.get_weather_by_coordinates(*coords)
            if weather_data:
                print("\nWeather data retrieved:")
                for key, value in weather_data.items():
                    print(f"{key}: {value}")
            else:
                print("Failed to get weather data")
        else:
            print("Failed to get coordinates")
        
        print("\n" + "=" * 50)

if __name__ == "__main__":
    test_weather() 