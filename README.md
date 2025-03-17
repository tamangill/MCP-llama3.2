# LLaMA Chat with Context

A Python-based chat interface for LLaMA that incorporates real-time weather and stock data into conversations.

## Features

- Interactive chat with LLaMA model through Ollama
- Real-time weather data integration using OpenWeather API
- Stock price information using Alpha Vantage API
- Natural language processing for query understanding
- Clean and simple command-line interface

## Prerequisites

- Python 3.7 or higher
- [Ollama](https://ollama.ai/) installed and running
- OpenWeather API key
- Alpha Vantage API key (optional, for stock data)

## Setup

1. Clone the repository:
   ```bash
   git clone [your-repo-url]
   cd llama-chat-context
   ```

2. Install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure API keys:
   - Copy `config.json.example` to `config.json`
   - Add your API keys to `config.json`:
     ```json
     {
         "openweather_api_key": "your_openweather_api_key",
         "alphavantage_api_key": "your_alphavantage_api_key"
     }
     ```

## Usage

1. Make sure Ollama is running with the LLaMA model installed
2. Run the chat interface:
   ```bash
   python3 chat_with_llama.py
   ```

3. Example queries:
   - Weather: "What's the weather like in London?"
   - Stocks: "What's the stock price of AAPL?"

## Testing

Run the test scripts to verify API connections:
```bash
python3 test_weather_api.py
python3 test_stock_api.py
python3 test_chat_system.py
```

## Project Structure

- `chat_with_llama.py`: Main chat interface
- `weather_context.py`: Weather data integration
- `stock_context.py`: Stock data integration
- `test_*.py`: Test files for each component
- `config.json`: API configuration file

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 