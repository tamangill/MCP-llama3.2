import requests
import json

def test_weather_api():
    # Load the API key from config.json
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            api_key = config.get('openweather_api_key')
    except Exception as e:
        print(f"Error loading config: {e}")
        return

    # API endpoint
    url = "http://api.openweathermap.org/data/2.5/weather"
    
    # Test parameters
    params = {
        "q": "London",
        "appid": api_key,
        "units": "metric"
    }
    
    print("\nTesting OpenWeather API connection...")
    print(f"API Key being used: {api_key}")
    
    try:
        response = requests.get(url, params=params)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("\nSuccess! API is working. Full response:")
            print(json.dumps(response.json(), indent=2))
        elif response.status_code == 401:
            print("\nError: Unauthorized. This usually means:")
            print("1. The API key is incorrect, or")
            print("2. The API key is new and hasn't been activated yet (takes ~2 hours)")
        elif response.status_code == 404:
            print("\nError: City not found")
        else:
            print(f"\nUnexpected status code: {response.status_code}")
            print("Response content:", response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"\nError connecting to the API: {e}")

if __name__ == "__main__":
    test_weather_api() 