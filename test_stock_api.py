import requests
import json

def test_stock_api():
    # Load the API key from config.json
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            api_key = config.get('alphavantage_api_key')
            if api_key == "YOUR_ALPHA_VANTAGE_API_KEY":
                print("\nError: Please replace 'YOUR_ALPHA_VANTAGE_API_KEY' in config.json with a real API key")
                print("Get a free API key from: https://www.alphavantage.co/support/#api-key")
                return
    except Exception as e:
        print(f"Error loading config: {e}")
        return

    # API endpoint
    url = "https://www.alphavantage.co/query"
    
    # Test parameters
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": "TSLA",  # Testing with Tesla stock
        "apikey": api_key
    }
    
    print("\nTesting Alpha Vantage API connection...")
    print(f"API Key: {api_key[:5]}...{api_key[-5:]} (showing first/last 5 chars)")
    print(f"Full URL being tested: {url}?function={params['function']}&symbol={params['symbol']}&apikey=XXXX")
    
    try:
        response = requests.get(url, params=params)
        print(f"\nStatus Code: {response.status_code}")
        
        try:
            data = response.json()
            print("\nResponse Data:", json.dumps(data, indent=2))
            
            if "Global Quote" in data and data["Global Quote"]:
                print("\nSuccess! Found stock data for TSLA")
            elif "Note" in data:
                print("\nAPI Limit Message:", data["Note"])
            else:
                print("\nNo stock data found. This could mean:")
                print("1. The API key is invalid")
                print("2. You've exceeded the API rate limit")
                print("3. The stock symbol is invalid")
            
        except json.JSONDecodeError:
            print("\nError: Could not parse JSON response")
            print("Raw response:", response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"\nError connecting to the API: {e}")

if __name__ == "__main__":
    test_stock_api() 