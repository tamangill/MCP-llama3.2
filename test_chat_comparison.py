"""
Test suite comparing responses between chat with llama and simple chat interfaces for US cities
"""
import unittest
import json
import datetime
from chat_with_llama import ChatInterface as LlamaChat
import simple_chat

class TestChatComparison(unittest.TestCase):
    def setUp(self):
        """Initialize chat interfaces and response log file"""
        with open("config.json") as f:
            self.config = json.load(f)
        
        self.llama_chat = LlamaChat()
        
        # Create a timestamped log file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = f"us_cities_comparison_{timestamp}.txt"
        
        # List of test queries for US cities
        self.test_queries = [
            # Major US cities
            ("what's the weather in New York, NY?", "New York,NY"),
            ("temperature in Los Angeles, CA?", "Los Angeles,CA"),
            ("how's the weather in Chicago, IL?", "Chicago,IL"),
            ("what's it like in Houston, TX?", "Houston,TX"),
            
            # Coastal cities
            ("weather in Miami, FL?", "Miami,FL"),
            ("what's the weather in Seattle, WA?", "Seattle,WA"),
            
            # Mountain cities
            ("temperature in Denver, CO?", "Denver,CO"),
            ("how's the weather in Salt Lake City, UT?", "Salt Lake City,UT"),
            
            # Desert cities
            ("what's it like in Phoenix, AZ?", "Phoenix,AZ"),
            ("weather in Las Vegas, NV?", "Las Vegas,NV")
        ]
        
        # Initialize the log file with header
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("US Cities Weather Response Comparison\n")
            f.write("=" * 50 + "\n")
            f.write(f"Test run started at: {timestamp}\n\n")

    def log_comparison(self, query, llama_response, simple_response):
        """Log the comparison results to file"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"\nQuery: {query}\n")
            f.write("-" * 50 + "\n")
            f.write("Llama Chat Response:\n")
            f.write(f"{llama_response}\n")
            f.write("-" * 25 + "\n")
            f.write("Simple Chat Response:\n")
            f.write(f"{simple_response}\n")
            f.write("=" * 50 + "\n")

    def test_weather_responses(self):
        """Compare and log weather responses from both interfaces"""
        # Common city abbreviations and alternates
        city_alternates = {
            'New York': ['ny', 'new york', 'nyc'],
            'Los Angeles': ['la', 'los angeles'],
            'Chicago': ['chi', 'chicago'],
            'Houston': ['houston'],
            'Miami': ['miami'],
            'Seattle': ['seattle'],
            'Denver': ['denver'],
            'Salt Lake City': ['salt lake', 'slc'],
            'Phoenix': ['phoenix', 'phx'],
            'Las Vegas': ['vegas', 'las vegas']
        }

        for query, city in self.test_queries:
            # Get responses from both interfaces
            llama_response = self.llama_chat.chat_with_model(query)
            simple_response = simple_chat.chat_with_model(query)
            
            # Log the comparison
            self.log_comparison(query, llama_response, simple_response)
            
            # Basic validation
            self.assertIsNotNone(llama_response)
            self.assertIsNotNone(simple_response)
            self.assertTrue(len(llama_response) > 0)
            self.assertTrue(len(simple_response) > 0)
            
            # Get the base city name (before any comma)
            base_city = city.split(',')[0]
            
            # Check if any of the city's alternate names are in the responses
            alternates = city_alternates.get(base_city, [base_city.lower()])
            
            # Check if at least one alternate form is present in each response
            llama_found = any(alt in llama_response.lower() for alt in alternates)
            simple_found = any(alt in simple_response.lower() for alt in alternates)
            
            self.assertTrue(llama_found, 
                          f"No variation of '{base_city}' found in Llama response")
            self.assertTrue(simple_found, 
                          f"No variation of '{base_city}' found in Simple response")

    def test_error_responses(self):
        """Compare and log error handling responses"""
        invalid_queries = [
            "what's the weather in FakeCity, XX?",
            "temperature in NotARealPlace, ZZ?",
            "weather in    , CA?",
            "what's it like in Area 51, NV?"
        ]
        
        for query in invalid_queries:
            llama_response = self.llama_chat.chat_with_model(query)
            simple_response = simple_chat.chat_with_model(query)
            
            # Log the comparison
            self.log_comparison(query, llama_response, simple_response)
            
            # Verify error responses
            self.assertIsNotNone(llama_response)
            self.assertIsNotNone(simple_response)

    def tearDown(self):
        """Add summary to log file"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write("\nTest Summary\n")
            f.write("-" * 20 + "\n")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"Test completed at: {timestamp}\n")
            f.write(f"Total US cities tested: {len(self.test_queries)}\n")
            f.write("Note: Full test results are available above\n")

if __name__ == '__main__':
    unittest.main(verbosity=2) 