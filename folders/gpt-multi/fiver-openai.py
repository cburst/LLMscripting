import os
import shutil
import time
import csv
import subprocess
import sys
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

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

            # Running a subprocess to process the file content
            command = [sys.executable, 'gpt.py', '-p', content, '--model', 'gpt-4o']
            output = subprocess.run(command, capture_output=True, text=True).stdout
            output_escaped = output.replace('"', '""')
            
            # Log the completion of the subprocess
            print(Fore.BLUE + f"Command completed for {i}.")  # Log command completion
            timestamp_output = datetime.now().strftime('%m-%d %H:%M:%S')
            print(Fore.CYAN + f"[{timestamp_output}] " + Style.BRIGHT + Fore.GREEN + f"(output size: {len(output)} characters)")  # Log output size
            print(Style.RESET_ALL, end="")  # Reset the color back to normal after the message

            # Writing results to CSV
            with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([os.path.basename(i), output_escaped])
                print(Fore.BLUE + f"Logged output to CSV for {i}")  # Log successful write to CSV

    # Log the end of processing
    print(Fore.CYAN + f"Finished processing all eligible files in {working_directory} using OPENAI LLM")

if __name__ == "__main__":
    main()