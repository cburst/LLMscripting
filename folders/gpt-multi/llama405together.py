import os
import argparse
from together import Together

def estimate_token_count(text):
    """Estimate the number of tokens in the text based on word count."""
    return len(text.split())

def chat_with_model(prompt):
    # Ensure the API key is set
    if not os.environ.get('TOGETHER_API_KEY'):
        raise EnvironmentError("API key not found. Please set the TOGETHER_API_KEY environment variable.")

    # Initialize the Together client
    client = Together(api_key=os.environ.get('TOGETHER_API_KEY'))

    # Estimate the number of tokens in the input prompt
    input_tokens = estimate_token_count(prompt)
    print(f"Estimated input tokens: {input_tokens}")  # Debugging statement

    # Set max_tokens ensuring the total doesn't exceed 4096 tokens
    max_tokens = max(1, 3096 - input_tokens)
    print(f"Calculated max tokens: {max_tokens}")  # Debugging statement

    # Make the request
    response_generator = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        messages=[{"role": "user", "content": prompt}],  # Use the prompt argument
        max_tokens=max_tokens,
        temperature=0.7,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
        stop=["\n\n"],
        stream=True
    )

    # Collect and print the response
    output = ""
    for response in response_generator:
        print(f"Response: {response}")  # Debug: print the entire response object
        if hasattr(response, 'choices') and response.choices:
            for choice in response.choices:
                if hasattr(choice, 'delta') and hasattr(choice.delta, 'content'):
                    output += choice.delta.content
                    print(f"Current output length: {len(output)}")  # Debug: print the current output length
                    print(f"Current output: {output}")  # Debug: print the current output content

    # Estimate the number of tokens in the output
    output_tokens = estimate_token_count(output)
    print(f"Final output tokens: {output_tokens}")  # Debugging statement

    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat with LLaMA 405 API via Together")
    parser.add_argument("prompt", type=str, help="The prompt to send to the model")
    args = parser.parse_args()

    output = chat_with_model(args.prompt)
    print(f"Final output: {output}")  # Print only the output