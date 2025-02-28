import requests
import json
import argparse

def chat_with_model(prompt, model, max_tokens):
    url = "http://localhost:1234/v1/completions"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=300)  # Set timeout to 300 seconds
        response.raise_for_status()  # Raise an error for bad HTTP status codes
        
        response_data = response.json()
        return response_data.get('choices', [])[0].get('text', '')

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat with LLM Studio model")
    parser.add_argument("prompt", type=str, help="The prompt to send to the model")
    parser.add_argument("--model", type=str, default="llama-3.1-8b-instruct", help="The model to use")
    parser.add_argument("--max_tokens", type=int, default=4096, help="Maximum number of tokens in the generated response")
    args = parser.parse_args()

    response = chat_with_model(args.prompt, args.model, args.max_tokens)
    if response:
        print(f"Model: {response}")
    else:
        print("No response or error occurred.")