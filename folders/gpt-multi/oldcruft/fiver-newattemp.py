import os
import shutil
import time
import csv
import sys
from datetime import datetime
from colorama import init, Fore, Style
import subprocess
import re

# Initialize colorama
init(autoreset=True)

# Function to remove control characters (ANSI escape sequences)
def remove_control_characters(text):
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    return ansi_escape.sub('', text)

# Function to clean the output by removing everything BEFORE and including lastline, and AFTER "Tokens:"
def process_output_file(raw_content):
    lines = raw_content.splitlines()

    # Initialize variables to track the secondlastline and lastline
    secondlastline_index = -1

    # Iterate backwards through the lines to find the last line with exactly one English letter and many spaces
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        # Check if the line contains exactly one English letter and many spaces
        if len(line) == 1 and line.isalpha():
            secondlastline_index = i
            break

    # If we found such a line and it's not the last line, we proceed
    if secondlastline_index != -1 and secondlastline_index < len(lines) - 1:
        lastline_index = secondlastline_index + 1

        # Remove all content before and including lastline
        cleaned_content = '\n'.join(lines[lastline_index + 1:])

        # Remove all content after and including "Tokens:"
        tokens_index = cleaned_content.find("Tokens:")
        if tokens_index != -1:
            cleaned_content = cleaned_content[:tokens_index].strip()

        # Clean ANSI escape sequences and other control characters
        cleaned_content = remove_control_characters(cleaned_content)

        return cleaned_content
    else:
        # If no valid lines found, just remove ANSI sequences
        return remove_control_characters(raw_content)

def main():
    if len(sys.argv) != 2:
        print(Fore.RED + "Usage: python script.py directory_path")
        sys.exit(1)

    file_directory = sys.argv[1]
    csv_file = f"{file_directory}.csv"
    working_directory = os.path.join(file_directory, "workingdirectory")

    os.makedirs(working_directory, exist_ok=True)

    if not os.path.exists(csv_file):
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            pass

    while True:
        all_files_met_condition = True
        total_missing_references = 0

        for file in os.listdir(file_directory):
            file_path = os.path.join(file_directory, file)
            if os.path.isfile(file_path) and get_file_size(file_path) > 10:
                filename = os.path.basename(file_path)
                count = count_occurrences(filename, csv_file)

                print(Fore.BLUE + f"File: {filename}, Count: {count}")

                if count < 5:
                    all_files_met_condition = False
                    total_missing_references += (5 - count)
                    if not os.path.exists(os.path.join(working_directory, filename)):
                        shutil.copy(file_path, working_directory)
                else:
                    if os.path.exists(os.path.join(working_directory, filename)):
                        os.remove(os.path.join(working_directory, filename))

        print(Fore.GREEN + f"Total number of remaining missing references: {total_missing_references}")

        if not all_files_met_condition:
            process_files(working_directory, csv_file)

        if all_files_met_condition:
            print(Fore.BLUE + "All files have appeared 5 times in the CSV.")
            break

        time.sleep(5)

def count_occurrences(filename, csv_file):
    count = 0
    with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if filename in row:
                count += 1
    return count

def get_file_size(file):
    return os.stat(file).st_size

def process_files(working_directory, csv_file):
    print(Fore.CYAN + f"Starting to process files in {working_directory}")

    for i in os.listdir(working_directory):
        i_path = os.path.join(working_directory, i)
        if os.path.isfile(i_path) and get_file_size(i_path) > 25:
            print(Fore.CYAN + f"Processing file: {i}")

            try:
                with open(i_path, 'r', encoding="utf-8", errors="ignore") as file:
                    content = file.read().replace('\x00', '')
                print(Fore.BLUE + f"Read content from {i}")
                timestamp_input = datetime.now().strftime('%m-%d %H:%M:%S')
                print(Fore.BLUE + f"[{timestamp_input}] (input size: {len(content)} characters)")
            except UnicodeDecodeError:
                print(Fore.RED + f"Error decoding file: {i_path}")
                continue

            # Start gpt.py as a subprocess only once
            gpt_process = start_gpt_session()

            # First prompt
            first_prompt = f"Can you check the following paragraph, located after the colon, for grammar errors, count the number of errors, place the number of grammar errors between @ symbols even if the number is zero (e.g, @0@, @1@, @2@, @3@, etc), explain each of the mistakes, and provide a revised paragraph. Start your answer with a line containing only the number of mistakes between two @ symbols. Here is the paragraph: {content}"

            first_output = send_prompt_and_capture_output(gpt_process, first_prompt, 1)

            # Second prompt
            second_prompt = "Next, please categorize those errors according to the following types of errors, even if the number of errors for a certain type is zero: Preposition errors (for these errors the delimiter is '!', for example !0!, !1!, etc), Morphology errors (for these errors the delimiter is '#', for example #0#, #1#, etc), Determiner errors (for these errors the delimiter is '€', for example €0€, €1€, etc), Tense/Aspect errors (for these errors the delimiter is '%', for example %0%, %1%, etc), Agreement errors (for these errors the delimiter is '^', for example ^0^, ^1^, etc), Syntax errors (for these errors the delimiter is '&', for example &0&, &1&, etc), Punctuation errors (for these errors the delimiter is '£', for example £0£, £1£, etc), Spelling errors (for these errors the delimiter is '~', for example ~0~, ~1~, etc), Unidiomatic errors (for these errors the delimiter is '+', for example +0+, +1+, etc), Multiple errors (for these errors the delimiter is '=', for example =0=, =1=, etc), and Miscellaneous errors (for these errors the delimiter is '₩', for example ₩0₩, ₩1₩, etc). Make sure that the sum total number matches the sum of the individual error types, using @ as the delimiter, as discussed earlier. Start your answer with all error numbers in their delimiters (even if the number of errors for a certain error type is 0), each separated by a space on the first line."

            second_output = send_prompt_and_capture_output(gpt_process, second_prompt, 2)

            # Third prompt
            third_prompt = "Are you sure there are no other errors? Please carefully double check. Start your answer with all updated error numbers in their delimiters (even if the number of errors for a certain error type is 0), each separated by a space on the first line. Then, proceed to describe all the errors detected, before and after double checking. Finally, provide a revised paragraph."

            third_output = send_prompt_and_capture_output(gpt_process, third_prompt, 3)

            # End gpt.py session
            end_gpt_session(gpt_process)

            # Save raw outputs to files before processing
            save_to_text_file('prompt01output.txt', first_output)
            save_to_text_file('prompt02output.txt', second_output)
            save_to_text_file('prompt03output.txt', third_output)

            # Process the output using the secondlastline and lastline approach
            first_output_processed = process_output_file(first_output)
            second_output_processed = process_output_file(second_output)
            third_output_processed = process_output_file(third_output)

            # Save the processed outputs to text files
            save_to_text_file('prompt01output-processed.txt', first_output_processed)
            save_to_text_file('prompt02output-processed.txt', second_output_processed)
            save_to_text_file('prompt03output-processed.txt', third_output_processed)

            # Writing results to CSV (only responses, not prompts)
            with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([os.path.basename(i), first_output_processed, second_output_processed, third_output_processed])
                print(Fore.BLUE + f"Logged output to CSV for {i}")

    print(Fore.CYAN + f"Finished processing all eligible files in {working_directory} using OPENAI LLM")

def start_gpt_session():
    # Get the full path to gpt.py (in the same directory as fiver.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory where fiver.py is located
    gpt_py_path = os.path.join(current_dir, "gpt.py")  # Full path to gpt.py

    # Ensure gpt.py exists
    if not os.path.exists(gpt_py_path):
        raise FileNotFoundError(f"gpt.py not found at {gpt_py_path}")

    # Command to run gpt.py with the correct model and arguments
    command = [sys.executable, gpt_py_path, "--model", "gpt-4o", "GrammarHelper"]

    # Start the gpt.py process, capturing only the output (stdout)
    gpt_process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,  # Allow input
        stdout=subprocess.PIPE,  # Capture output
        stderr=subprocess.PIPE,  # Capture errors
        text=True  # Ensure text mode
    )
    return gpt_process

def send_prompt_and_capture_output(gpt_process, prompt, prompt_number):
    # Send the prompt to the already running gpt.py process
    gpt_process.stdin.write(prompt + "\n")
    gpt_process.stdin.flush()

    response = ''
    total_characters = 0  # Track total number of characters received
    prompt_label = f"Prompt {prompt_number:02d} characters received: "

    try:
        # Continuously read the output from the process
        while True:
            output = gpt_process.stdout.readline()
            if output:
                response += output
                total_characters += len(output)  # Count received characters

                # Print the total number of characters received in real-time
                sys.stdout.write(f"\r{Fore.YELLOW}{prompt_label}{total_characters}")
                sys.stdout.flush()

            # Break when "Tokens:", "Price:", or "Total:" is detected in the output
            if "Tokens:" in output or "Price:" in output or "Total:" in output:
                break

        print()  # Print a new line after finishing reading the prompt

    except Exception as e:
        print(f"Error occurred: {e}")

    return response

def end_gpt_session(gpt_process):
    gpt_process.stdin.write("exit\n")
    gpt_process.stdin.flush()
    gpt_process.terminate()

def save_to_text_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

if __name__ == "__main__":
    main()