import urllib.request
import json
import os
import ssl
import argparse

def allowSelfSignedHttps(allowed):
    # Bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True) # This line is needed if you use self-signed certificate in your scoring service.

def chat_with_model(prompt, api_url, api_key, temperature=0.8, top_p=0.1, best_of=1, presence_penalty=0.0, use_beam_search=False, ignore_eos=False, skip_special_tokens=False):
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'}

    # Calculate max tokens based on input length
    max_context_length = 4096  # Maximum allowed tokens for the model
    input_tokens = len(prompt.split())  # Simple token estimation by splitting on spaces
    max_tokens = max_context_length - input_tokens

    if max_tokens <= 0:
        print("The input prompt is too long for the context window.")
        return

    data = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "best_of": best_of,
        "presence_penalty": presence_penalty,
        "use_beam_search": str(use_beam_search).lower(),
        "ignore_eos": str(ignore_eos).lower(),
        "skip_special_tokens": str(skip_special_tokens).lower()
    }

    body = str.encode(json.dumps(data))

    req = urllib.request.Request(api_url, body, headers)

    try:
        response = urllib.request.urlopen(req)
        result = response.read().decode('utf-8')  # Decode the byte string to a JSON string
        result_json = json.loads(result)  # Parse the JSON string into a Python dictionary
        
        # Extract and print the relevant information
        choices = result_json.get('choices', [])
        if choices:
            message_content = choices[0].get('message', {}).get('content', '')
            print(message_content)
        else:
            print("No choices found in the response.")

    except urllib.error.HTTPError as error:
        print("The request failed with status code:", error.code)
        print(error.info())
        print(error.read().decode("utf8", 'ignore'))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat with Azure AI model")
    parser.add_argument("prompt", type=str, help="The prompt to send to the model")
    parser.add_argument("--api_url", type=str, default="https://Meta-Llama-3-1-405B-Instruct-ekk.eastus2.models.ai.azure.com/v1/chat/completions", help="The API endpoint URL")
    parser.add_argument("--temperature", type=float, default=0.8, help="Sampling temperature")
    parser.add_argument("--top_p", type=float, default=0.1, help="Nucleus sampling probability")
    parser.add_argument("--best_of", type=int, default=1, help="Number of best outputs")
    parser.add_argument("--presence_penalty", type=float, default=0.0, help="Presence penalty")
    parser.add_argument("--use_beam_search", type=bool, default=False, help="Use beam search")
    parser.add_argument("--ignore_eos", type=bool, default=False, help="Ignore end-of-sequence tokens")
    parser.add_argument("--skip_special_tokens", type=bool, default=False, help="Skip special tokens")
    args = parser.parse_args()

    # Get API key from environment variable
    api_key = os.getenv("AZURE_API_KEY")
    if not api_key:
        raise Exception("API key not found. Please set the AZURE_API_KEY environment variable.")

    chat_with_model(args.prompt, args.api_url, api_key, args.temperature, args.top_p, args.best_of, args.presence_penalty, args.use_beam_search, args.ignore_eos, args.skip_special_tokens)