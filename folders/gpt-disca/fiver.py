import os
import shutil
import time
import csv
import sys
from datetime import datetime
from colorama import init, Fore, Style
import subprocess
import re
import select
import signal

# Initialize colorama
init(autoreset=True)

# Function to remove control characters (ANSI escape sequences)
def remove_control_characters(text):
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    return ansi_escape.sub('', text)

# Function to clean the output by removing everything BEFORE and including lastline, and AFTER "Tokens:"
def process_output_file(raw_content):
    lines = raw_content.splitlines()
    secondlastline_index = -1

    # Find the last line with exactly one English letter and spaces
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        if len(line) == 1 and line.isalpha():
            secondlastline_index = i
            break

    if secondlastline_index != -1 and secondlastline_index < len(lines) - 1:
        lastline_index = secondlastline_index + 1
        cleaned_content = '\n'.join(lines[lastline_index + 1:])
        tokens_index = cleaned_content.find("Tokens:")
        if tokens_index != -1:
            cleaned_content = cleaned_content[:tokens_index].strip()
        return remove_control_characters(cleaned_content)
    else:
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
                
                # Truncate content to the first 3650 characters if it exceeds this length
                content = content[:3650]

                print(Fore.BLUE + f"Read content from {i} (truncated to {len(content)} characters)")
                timestamp_input = datetime.now().strftime('%m-%d %H:%M:%S')
                print(Fore.BLUE + f"[{timestamp_input}] (input size: {len(content)} characters)")
            except UnicodeDecodeError:
                print(Fore.RED + f"Error decoding file: {i_path}")
                continue

            # Start gpt.py as a subprocess only once
            gpt_process = start_gpt_session()

            # First prompt
            first_prompt = f"Can you perform sentiment analysis on the following paragraph, referred to as 'the sample text' in subsequent queries, by replying with any and all words contained in the sample text with POSITIVE connotations, each separated by commas, no other text whatsoever (especially no introduction or conclusion sentences, as these will disrupt the analysis process). Here is the paragraph: {content}"

            first_output, gpt_process = send_prompt_and_capture_output(gpt_process, first_prompt, 1)

            # Second prompt
            second_prompt = "Can you perform sentiment analysis on 'the sample text', by replying with any and all words contained in the sample text with NEGATIVE connotations, each separated by commas, no other text whatsoever (especially no introduction or conclusion sentences, as these will disrupt the analysis process)."

            second_output, gpt_process = send_prompt_and_capture_output(gpt_process, second_prompt, 2)

            # Third prompt
            third_prompt = "On a scale from -1 to +1, with -1 being completely negative and +1 being completely positive, how would you rate the sample text. reply with only numerals, a single decimal point, and a plus or minus symbol, no other characters whatsoever (especially no introduction or conclusion sentences, as these will disrupt the analysis process)."

            third_output, gpt_process = send_prompt_and_capture_output(gpt_process, third_prompt, 3)

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
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory where fiver.py is located
    gpt_py_path = os.path.join(current_dir, "gpt.py")  # Full path to gpt.py

    if not os.path.exists(gpt_py_path):
        raise FileNotFoundError(f"gpt.py not found at {gpt_py_path}")

    command = [sys.executable, gpt_py_path, "--model", "gpt-4o", "Disca"]

    gpt_process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        preexec_fn=os.setsid  # Ensures a new session on Unix-like systems
    )
    return gpt_process

def send_prompt_and_capture_output(gpt_process, prompt, prompt_number):
    try:
        gpt_process.stdin.write(prompt + "\n")
        gpt_process.stdin.flush()
    except BrokenPipeError:
        print(Fore.RED + f"\nError: Broken pipe for prompt {prompt_number}. Restarting process.")
        gpt_process = start_gpt_session()  # Restart if broken
        gpt_process.stdin.write(prompt + "\n")
        gpt_process.stdin.flush()

    response_lines = []  # Store all output lines
    total_characters = 0
    prompt_label = f"Prompt {prompt_number:02d} characters received: "

    start_time = time.time()

    try:
        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time > 20:
                print(Fore.RED + f"\nPrompt {prompt_number} timed out. Restarting process for next prompt.")
                response_lines = ["SKIPPED: TIMED OUT"]
                os.killpg(os.getpgid(gpt_process.pid), signal.SIGKILL)
                gpt_process = start_gpt_session()
                break

            ready, _, _ = select.select([gpt_process.stdout], [], [], 1)
            if ready:
                output = gpt_process.stdout.readline()
                if output:
                    response_lines.append(output.strip())
                    total_characters += len(output)

                    sys.stdout.write(f"\r{Fore.YELLOW}{prompt_label}{total_characters}")
                    sys.stdout.flush()

                    if "Tokens:" in output or "Price:" in output or "Total:" in output:
                        break
        print()  

    except Exception as e:
        print(f"Error occurred: {e}")

    final_response = response_lines[-2] if len(response_lines) >= 2 else (response_lines[-1] if response_lines else "SKIPPED: TIMED OUT")
    return final_response, gpt_process

def end_gpt_session(gpt_process):
    gpt_process.stdin.write("exit\n")
    gpt_process.stdin.flush()
    gpt_process.terminate()

def save_to_text_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

if __name__ == "__main__":
    main()