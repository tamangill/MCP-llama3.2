import unittest
from chat_with_llama import extract_stock_symbol, extract_city_from_query, load_config
from stock_context import StockContext
import json
import requests
from typing import Dict

class TestChatSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests"""
        config = load_config()
        cls.stock_context = StockContext(config.get('alphavantage_api_key', ''))

    def test_stock_symbol_extraction_basic(self):
        """Test basic stock symbol extraction"""
        queries = [
            ("what's the stock price of AAPL?", "aapl"),
            ("TSLA stock price", "tsla"),
            ("how much is MSFT trading at?", "msft"),
            ("stock price for GOOGL", "googl"),
        ]
        for query, expected in queries:
            self.assertEqual(extract_stock_symbol(query), expected)

    def test_stock_symbol_extraction_invalid(self):
        """Test invalid stock queries return empty string"""
        queries = [
            "what's the weather like?",
            "hello world",
            "stock",
            "price",
        ]
        for query in queries:
            self.assertEqual(extract_stock_symbol(query), "")

    def test_weather_query_extraction(self):
        """Test weather city extraction"""
        queries = [
            ("what's the weather like in London?", "london"),
            ("weather in New York", "new york"),
            ("how's the weather in Paris?", "paris"),
        ]
        for query, expected in queries:
            self.assertEqual(extract_city_from_query(query), expected)

    def test_stock_api_connection(self):
        """Test connection to Alpha Vantage API"""
        response = self.stock_context.get_stock_quote("AAPL")
        self.assertIsNotNone(response)
        self.assertIsInstance(response, Dict)

    def test_stock_data_format(self):
        """Test stock data format is correct"""
        data = self.stock_context.get_stock_quote("MSFT")
        if data:  # Only test if we got data (might fail due to API limits)
            required_fields = ["symbol", "price", "change", "change_percent", "volume", "timestamp"]
            for field in required_fields:
                self.assertIn(field, data)

    def test_invalid_stock_symbol(self):
        """Test handling of invalid stock symbols"""
        response = self.stock_context.get_stock_quote("INVALID_SYMBOL")
        self.assertIsNone(response)

    def test_stock_context_generation(self):
        """Test stock context string generation"""
        context = self.stock_context.generate_stock_context("AAPL")
        self.assertIsInstance(context, str)
        self.assertGreater(len(context), 0)

    def test_config_loading(self):
        """Test configuration loading"""
        config = load_config()
        self.assertIsInstance(config, dict)
        self.assertIn('alphavantage_api_key', config)
        self.assertIn('openweather_api_key', config)

    def test_multiple_stock_queries(self):
        """Test multiple stock queries in succession"""
        symbols = ["AAPL", "MSFT", "GOOGL"]
        for symbol in symbols:
            data = self.stock_context.get_stock_quote(symbol)
            if data:  # Only assert if we got data (might fail due to API limits)
                self.assertEqual(data["symbol"], symbol)

    def test_rate_limit_handling(self):
        """Test handling of API rate limits"""
        # Make multiple rapid requests to trigger rate limit
        responses = []
        for _ in range(5):  # Alpha Vantage free tier allows 5 requests per minute
            response = self.stock_context.get_stock_quote("AAPL")
            responses.append(response is not None)
        
        # At least one request should succeed
        self.assertTrue(any(responses))

def main():
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestChatSystem)
    
    # Run tests
    print("\nRunning chat system tests...")
    print("Note: Some tests may be skipped due to API rate limits")
    print("-------------------------------------------")
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    main() 