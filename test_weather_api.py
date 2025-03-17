import requests
import json

def test_location_formats():
    """Test different location format options"""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            api_key = config.get('openweather_api_key')
    except Exception as e:
        print(f"Error loading config: {e}")
        return

    # Test locations in different formats
    test_locations = [
        "London",                    # City only
        "London, GB",               # City, Country
        "Los Angeles, CA",          # City, State (abbreviated)
        "Los Angeles, California",  # City, State (full name)
        "Los Angeles, CA, US",      # City, State, Country
        "Paris, FR",                # International city with country
        "New York, NY, US",         # US city with state and country
        "Tokyo, JP"                 # International city with country
    ]
    
    geocoding_url = "http://api.openweathermap.org/geo/1.0/direct"
    
    print("\nTesting different location formats...")
    print("=====================================")
    
    for location in test_locations:
        print(f"\nTesting location: '{location}'")
        
        params = {
            "q": location,
            "limit": 1,
            "appid": api_key
        }
        
        try:
            response = requests.get(geocoding_url, params=params)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    result = data[0]
                    print("Found:")
                    print(f"- Name: {result.get('name', 'N/A')}")
                    print(f"- State: {result.get('state', 'N/A')}")
                    print(f"- Country: {result.get('country', 'N/A')}")
                    print(f"- Coordinates: {result.get('lat', 'N/A')}°N, {result.get('lon', 'N/A')}°E")
                else:
                    print("No results found")
            else:
                print(f"Error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"Error: {str(e)}")
        
        print("-" * 40)

def test_weather_api():
    """Test weather data retrieval for a specific location"""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            api_key = config.get('openweather_api_key')
    except Exception as e:
        print(f"Error loading config: {e}")
        return

    # Test with a specific location
    location = "London, GB"  # Using city with country code for precision
    
    # Test Geocoding API first
    print(f"\nTesting weather retrieval for '{location}'")
    print("=====================================")
    
    geocoding_url = "http://api.openweathermap.org/geo/1.0/direct"
    geocoding_params = {
        "q": location,
        "limit": 1,
        "appid": api_key
    }
    
    try:
        geocoding_response = requests.get(geocoding_url, params=geocoding_params)
        print(f"\nGeocoding Status Code: {geocoding_response.status_code}")
        
        if geocoding_response.status_code == 200:
            locations = geocoding_response.json()
            if locations:
                location_data = locations[0]
                print("\nGeocoding Success! Location data:")
                print(f"City: {location_data.get('name')}")
                print(f"State: {location_data.get('state', 'N/A')}")
                print(f"Country: {location_data.get('country')}")
                print(f"Coordinates: {location_data.get('lat'):.4f}°N, {location_data.get('lon'):.4f}°E")
                
                # Now test weather API with these coordinates
                print("\nTesting Weather API with coordinates...")
                weather_url = "http://api.openweathermap.org/data/2.5/weather"
                weather_params = {
                    "lat": location_data['lat'],
                    "lon": location_data['lon'],
                    "appid": api_key,
                    "units": "metric"
                }
                
                weather_response = requests.get(weather_url, params=weather_params)
                print(f"Weather API Status Code: {weather_response.status_code}")
                
                if weather_response.status_code == 200:
                    weather_data = weather_response.json()
                    print("\nWeather API Success! Full response:")
                    print(json.dumps(weather_data, indent=2))
                else:
                    print("\nError fetching weather data")
                    print("Response content:", weather_response.text)
            else:
                print(f"\nNo location data found for '{location}'")
        elif geocoding_response.status_code == 401:
            print("\nError: Unauthorized. This usually means:")
            print("1. The API key is incorrect, or")
            print("2. The API key is new and hasn't been activated yet (takes ~2 hours)")
        else:
            print(f"\nUnexpected geocoding status code: {geocoding_response.status_code}")
            print("Response content:", geocoding_response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"\nError connecting to the API: {e}")

if __name__ == "__main__":
    print("Testing location format options...")
    test_location_formats()
    print("\n\nTesting full weather retrieval...")
    test_weather_api() 