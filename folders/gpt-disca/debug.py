import sys
import subprocess

def read_file_content(file_path):
    with open(file_path, 'r') as file:
        return file.read()

if __name__ == "__main__":
    # Ensure the script is called with the correct number of arguments
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <file_path>")
        sys.exit(1)

    # Get the file path from the arguments
    file_path = sys.argv[1]

    try:
        # Read the content of the file
        content = read_file_content(file_path)
    except Exception as e:
        print(f"Failed to read the file: {e}", file=sys.stderr)
        sys.exit(1)

    # Define your command and arguments
    command = [sys.executable, 'gpt.py', '-p', content, '--model', 'gpt-4o']

    # Print the command for debugging
    print("Running command:", ' '.join(command))

    try:
        # Run the command
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        # Print the output
        print("Standard Output:\n", result.stdout)
        print("Standard Error:\n", result.stderr)
    except subprocess.CalledProcessError as e:
        # Handle errors
        print(f"Error occurred: {e.stderr}", file=sys.stderr)
    except Exception as e:
        # Handle unexpected exceptions
        print(f"An unexpected error occurred: {str(e)}", file=sys.stderr)