import os
import shutil
import time
import csv
import subprocess
import sys
from datetime import datetime
from colorama import init, Fore, Style
import pexpect
import re

# Initialize colorama
init(autoreset=True)

# Function to remove control characters (ANSI escape sequences) using the provided regular expression
def remove_control_characters(text):
    # Regular expression to match ANSI escape sequences
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    return ansi_escape.sub('', text)

def main():
    # Check if the directory argument is provided
    if len(sys.argv) != 2:
        print(Fore.RED + "Usage: python script.py directory_path")
        sys.exit(1)

    file_directory = sys.argv[1]
    csv_file = f"{file_directory}.csv"
    working_directory = os.path.join(file_directory, "workingdirectory")

    # Create working directory if it doesn't exist
    os.makedirs(working_directory, exist_ok=True)

    # Create CSV file if it doesn't exist
    if not os.path.exists(csv_file):
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            pass

    while True:
        all_files_met_condition = True
        total_missing_references = 0

        # Loop through each file in the directory
        for file in os.listdir(file_directory):
            file_path = os.path.join(file_directory, file)
            if os.path.isfile(file_path) and get_file_size(file_path) > 10:
                filename = os.path.basename(file_path)
                count = count_occurrences(filename, csv_file)

                print(Fore.BLUE + f"File: {filename}, Count: {count}")  # Debugging line

                if count < 5:
                    all_files_met_condition = False
                    total_missing_references += (5 - count)
                    # Copy file to working directory if not already there
                    if not os.path.exists(os.path.join(working_directory, filename)):
                        shutil.copy(file_path, working_directory)
                else:
                    # Delete file from working directory if it's there
                    if os.path.exists(os.path.join(working_directory, filename)):
                        os.remove(os.path.join(working_directory, filename))

        print(Fore.GREEN + f"Total number of remaining missing references: {total_missing_references}")

        # Run the file processing only if any file needs processing
        if not all_files_met_condition:
            process_files(working_directory, csv_file)

        # Check if the condition is met for all files
        if all_files_met_condition:
            print(Fore.BLUE + "All files have appeared 5 times in the CSV.")
            break

        # Optional: Add a delay to avoid rapid, continuous execution
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
    # Log the start of processing
    print(Fore.CYAN + f"Starting to process files in {working_directory}")

    for i in os.listdir(working_directory):
        i_path = os.path.join(working_directory, i)
        if os.path.isfile(i_path) and get_file_size(i_path) > 25:
            print(Fore.CYAN + f"Processing file: {i}")  # Log the file being processed

            try:
                with open(i_path, 'r', encoding="utf-8", errors="ignore") as file:
                    content = file.read().replace('\x00', '')  # Remove null bytes
                print(Fore.BLUE + f"Read content from {i}")  # Log file read success
                timestamp_input = datetime.now().strftime('%m-%d %H:%M:%S')
                print(Fore.BLUE + f"[{timestamp_input}] (input size: {len(content)} characters)")  # Log input size
            except UnicodeDecodeError:
                print(Fore.RED + f"Error decoding file: {i_path}")  # Log decoding error
                continue

            # Start the interactive session
            child = start_gpt_session()

            # Add the instruction to the first prompt
            instruction = "Can you check the following paragraph, located after the colon, for grammar errors, count the number of errors, place the number of grammar errors between @ symbols even if the number is zero (e.g, @0@, @1@, @2@, @3@, etc), explain each of the mistakes, and provide a revised paragraph. Start your answer with a line containing only the number of mistakes between two @ symbols. Here is the paragraph: "
            first_prompt = instruction + content

            # Process the content with the first prompt
            first_output = send_prompt_and_capture_output(child, first_prompt)

            # Process the "Double check that." prompt
            second_output = send_prompt_and_capture_output(child, "Next, please categorize those errors according to the following types of errors, even if the number of errors for a certain type is zero: Preposition errors (for these errors the delimiter is '!', for example !0!, !1!, etc), Morphology errors (for these errors the delimiter is '#', for example #0#, #1#, etc), Determiner errors (for these errors the delimiter is '€', for example €0€, €1€, etc), Tense/Aspect errors (for these errors the delimiter is '%', for example %0%, %1%, etc), Agreement errors (for these errors the delimiter is '^', for example ^0^, ^1^, etc), Syntax errors (for these errors the delimiter is '&', for example &0&, &1&, etc), Punctuation errors (for these errors the delimiter is '£', for example £0£, £1£, etc), Spelling errors (for these errors the delimiter is '~', for example ~0~, ~1~, etc), Unidiomatic errors (for these errors the delimiter is '+', for example +0+, +1+, etc), Multiple errors (for these errors the delimiter is '=', for example =0=, =1=, etc), and Miscellaneous errors (for these errors the delimiter is '₩', for example ₩0₩, ₩1₩, etc). Make sure that the sum total number matches the sum of the individual error types, using @ as the delimiter, as discussed earlier. Start your answer with all error numbers in their delimiters (even if the number of errors for a certain error type is 0), each separated by a space on the first line.")

            # Process the third prompt "Are you sure there are no other errors? Please carefully double check."
            third_output = send_prompt_and_capture_output(child, "Are you sure there are no other errors? Please carefully double check. Start your answer with all updated error numbers in their delimiters (even if the number of errors for a certain error type is 0), each separated by a space on the first line.")

            # Fourth prompt: Translate text to Korean except for checked and revised text
            fourth_output = send_prompt_and_capture_output(child, "Please translate all text from the previous message into Korean, except for the text that was checked and the revised text. Specifically, all of the grammar errors should be clearly explained in Korean to benefit Korean learners of English.")

            # End the session after processing all prompts
            end_gpt_session(child)

            # Writing results to CSV
            with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([os.path.basename(i), first_output, second_output, third_output, fourth_output])
                print(Fore.BLUE + f"Logged output to CSV for {i}")  # Log successful write to CSV

    # Log the end of processing
    print(Fore.CYAN + f"Finished processing all eligible files in {working_directory} using OPENAI LLM")
    
def start_gpt_session():
    command = f"{sys.executable} gpt.py --model gpt-4o GrammarHelper"
    child = pexpect.spawn(command, echo=False)
    child.timeout = 120  # Set timeout for long responses
    child.expect(r'>')  # Wait for the initial prompt (">")
    return child

def send_prompt_and_capture_output(child, prompt):
    child.sendline(prompt)
    child.expect(r'Tokens:')
    response = child.before.decode('utf-8')

    # Post-process the output using the new logic
    start_index_1 = response.rfind("[1A[2K[32m")
    start_index_2 = response.rfind("[J[?7h")
    start_index = max(start_index_1, start_index_2)
    end_index = response.rfind("[0m[2m")
    
    if start_index != -1 and end_index != -1:
        final_output = response[start_index + len("[1A[2K[32m"):end_index].strip()
        
        # Remove specific control sequences
        final_output = final_output.replace("[0m", "").replace("[32m", "")
        final_output = final_output.replace("[1;33m", "").replace("[1;32m", "")
        final_output = final_output.replace("[3;32m1", "").replace("[1;32m", "")
        
        # Remove all remaining ANSI control sequences using the new regular expression
        final_output = remove_control_characters(final_output)
    else:
        final_output = remove_control_characters(response.strip())

    return final_output

def end_gpt_session(child):
    child.sendline('exit')
    child.close()

if __name__ == "__main__":
    main()