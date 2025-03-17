import requests
import sys

def chat_with_model(prompt: str, model: str = "llama3.2:latest") -> str:
    """
    Send a prompt to the Ollama API and get the response
    """
    try:
        response = requests.post('http://localhost:11434/api/generate',
                               json={
                                   "model": model,
                                   "prompt": prompt,
                                   "stream": False
                               })
        response.raise_for_status()
        return response.json()['response']
    except requests.exceptions.RequestException as e:
        print(f"\nError communicating with Ollama: {e}")
        return None
    except KeyError as e:
        print(f"\nUnexpected response format: {e}")
        return None

def main():
    print("Welcome to Simple LLaMA Chat! (Press Ctrl+C to exit)")
    print("-------------------------------------------")
    print("Just type your message and press Enter")
    print("-------------------------------------------\n")
    
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            # Get response from model
            print("\nThinking...")
            response = chat_with_model(user_input)
            
            if response:
                print("\nLLaMA:", response)
            else:
                print("\nError: Failed to get response from the model")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main() 