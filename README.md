# LLaMA Chat with Multiple Personalities

A Python-based chat interface for LLaMA that incorporates real-time weather and stock data, with support for multiple personality styles including Surrey Jack and Sidhu Moosewala.

## Features

- Interactive chat with LLaMA model through Ollama
- Multiple personality options:
  - Surrey Jack: Authentic Surrey/Vancouver slang and culture
  - Sidhu Moosewala: Punjabi artist style with bilingual responses
- Real-time weather data using OpenWeather API
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

## Available Chat Personalities

### Surrey Jack Style
Run with:
```bash
python3 chat_with_llama.py
```

Features:
- Surrey/Vancouver area slang
- Local cultural references
- Street-style responses
- Example queries:
  - "What's the weather like in Surrey?"
  - "How's Tesla stock doing fam?"

### Sidhu Moosewala Style
Run with:
```bash
python3 chat_with_sidhu.py
```

Features:
- Bilingual responses (Punjabi-English mix)
- References to Punjabi culture and music
- Village life and traditional values
- Example queries:
  - "Mansa da weather ki kehnda?" (How's the weather in Mansa?)
  - "Tesla de shares kiddan ja rahe ne?" (How are Tesla shares doing?)

## Example Interactions

### Surrey Jack Style:
```
You: what's the weather in surrey?
Your boy: Yo fam, lemme check that for you real quick! Weather in Surrey's looking mod today...
```

### Sidhu Moosewala Style:
```
Tusi: pind ch ki haal ne?
Sidhu: Kiddan paaji! Apne pind ch mausam ekdum vadiya aa...
```

## Project Structure

- `chat_with_llama.py`: Surrey Jack personality interface
- `chat_with_sidhu.py`: Sidhu Moosewala personality interface
- `weather_context.py`: Weather data integration
- `stock_context.py`: Stock data integration
- `personalities/`: Personality configuration files
  - `surrey_jack.py`: Surrey Jack personality
  - `sidhu_moosewala.py`: Sidhu Moosewala personality
- `test_*.py`: Test files for each component
- `config.json`: API configuration file

## Testing

Run the test scripts to verify API connections:
```bash
python3 test_weather_api.py
python3 test_stock_api.py
python3 test_chat_system.py
```

## Contributing

Contributions are welcome! Feel free to:
- Add new personalities
- Improve existing personalities
- Enhance API integrations
- Fix bugs or improve documentation

## License

MIT License - feel free to use and modify as needed. 