import subprocess
import time
import csv
import glob
import sys
import os
import re
import shutil

def get_ordinal_suffix(n):
    """
    Return the ordinal suffix for an integer n: '1st', '2nd', '3rd', etc.
    """
    # Special cases
    if 11 <= (n % 100) <= 13:
        return f"{n}th"
    # General cases
    last_digit = n % 10
    if last_digit == 1:
        return f"{n}st"
    elif last_digit == 2:
        return f"{n}nd"
    elif last_digit == 3:
        return f"{n}rd"
    else:
        return f"{n}th"

# Set the script's directory as the working directory.
script_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_directory)

# Ensure a directory is provided as an argument.
if len(sys.argv) < 2:
    print("Usage: python script.py <directory>")
    sys.exit(1)

input_directory = sys.argv[1].rstrip("/")  # Remove trailing slash if present
if not os.path.isdir(input_directory):
    print("The provided argument is not a valid directory.")
    sys.exit(1)

# New delimiter instruction.
new_delimiter_instruction = "start your response with <<start>> and end your response with <<end>>."

# Path to the GPT log file.
log_file_path = "gptcli.log"

# Get base prompts from prompt*.txt in the current directory.
prompt_files = sorted(glob.glob("prompt*.txt"))
if not prompt_files:
    print("No prompt files found in the current directory.")
    sys.exit(1)

base_prompts = []
for prompt_file in prompt_files:
    with open(prompt_file, "r", encoding="utf-8") as f:
        base_prompts.append(f.read().strip())

num_prompts = len(base_prompts)
print(f"Number of base prompts found: {num_prompts}")

# Get text files from the provided directory.
text_files = sorted(glob.glob(os.path.join(input_directory, "*.txt")))
num_text_files = len(text_files)
print(f"Number of text files found in {input_directory}: {num_text_files}")

def count_token_usage(log_file):
    """Count occurrences of 'Token usage' in the log file."""
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            return len(re.findall(r"Token usage", f.read()))
    return 0

def wait_for_responses(expected_count, timeout=120):
    """
    Wait until the number of 'Token usage' strings in the log file
    matches the expected count. Retries until the timeout is reached.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        time.sleep(2)  # Check every 2 seconds
        current_count = count_token_usage(log_file_path)
        if current_count >= expected_count:
            return True  # Success, we got all responses
    return False  # Timeout reached

def extract_responses_and_save(filename, iteration_successful_csvs):
    """
    Extract responses from gptcli.log and save them to filename.csv 
    with preserved line breaks. 
    """
    if not os.path.exists(log_file_path):
        print(f"Error: Log file for {filename} not found.")
        return False

    with open(log_file_path, "r", encoding="utf-8") as log_file:
        log_data = log_file.read()

        # Extract responses using assistant messages
        matches = re.findall(
            r"gptcli-session - INFO - assistant:.*?<<start>>(.*?)<<end>>",
            log_data, 
            re.DOTALL
        )

        # Ensure correct response count
        if len(matches) < num_prompts:
            print(f"Error: Missing responses for {filename}. Expected {num_prompts}, but got {len(matches)}.")
            return False

        # Preserve line breaks inside responses
        responses = [resp.strip() for resp in matches]

    csv_file = os.path.join(input_directory, f"{filename}.csv")
    header = ["filename"] + [f"prompt{str(i+1).zfill(2)}" for i in range(num_prompts)]

    with open(csv_file, mode="w", newline="", encoding="utf-8") as f_csv:
        writer = csv.writer(f_csv, quoting=csv.QUOTE_ALL)  # quote all fields
        writer.writerow(header)  # Write header
        writer.writerow([filename] + responses)

    print(f"CSV file saved: {csv_file}")
    iteration_successful_csvs.append(csv_file)
    return True

def process_text_file(input_file, base_prompts, new_delimiter_instruction, iteration_successful_csvs):
    """
    Runs a GPT session for a single text file and handles up to 10 retries 
    if there's a timeout waiting for responses. 
    Returns True if processing eventually succeeds, otherwise False.
    """
    filename = os.path.splitext(os.path.basename(input_file))[0]
    failure_counter = 0

    while failure_counter < 10:
        # Move old log file instead of deleting it
        if os.path.exists(log_file_path):
            error_logfile = os.path.join(
                input_directory, f"gptcli_{filename}_error{failure_counter + 1}.log"
            )
            shutil.move(log_file_path, error_logfile)
            print(f"Saved failed attempt log: {error_logfile}")

        with open(input_file, "r", encoding="utf-8") as f_in:
            file_text = f_in.read().strip()

        # Start a new GPT process for this file
        process = subprocess.Popen(
            ["gpt", "--model", "gpt-4o", "GrammarHelper"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        # Read the initial prompt from GPT
        process.stdout.readline()

        # Send each base_prompt
        for i, base_prompt in enumerate(base_prompts):
            if i == 0:
                full_prompt = f"{new_delimiter_instruction} {base_prompt} {file_text}"
            else:
                full_prompt = f"{new_delimiter_instruction} {base_prompt}"

            # Remove any quotation marks from the prompt.
            full_prompt = full_prompt.replace('"', '')

            # Send the prompt.
            process.stdin.write(full_prompt + "\n")
            process.stdin.flush()

            # Wait for the response before sending the next prompt
            success = wait_for_responses(i + 1)
            if not success:
                print(f"Error: Timeout waiting for response {i + 1} for {filename}. Retrying...")
                failure_counter += 1
                process.kill()
                break  # Restart the GPT process
        else:
            # If we didn't break out early, we got all prompts
            process.stdin.write(":q\n")
            process.stdin.flush()
            process.communicate()

            # Extract responses and save CSV
            if extract_responses_and_save(filename, iteration_successful_csvs):
                # Rename log file to preserve it
                new_logfile = os.path.join(input_directory, f"gptcli_{filename}.txt")
                shutil.move(log_file_path, new_logfile)
                print(f"Renamed log file: {new_logfile}")
                return True  # success
            else:
                print(f"Error processing {filename}, retrying...")
                failure_counter += 1

    print(f"Error: Reached max retries (10) for {filename}.")
    return False

def move_non_txt_files_into_subfolder(input_directory, subfolder_name, original_txt_files):
    """
    Move every file in `input_directory` except the original TXT files
    into a subdirectory named `subfolder_name`. If a file with the same name exists in
    the destination, it will be overwritten.
    """
    subfolder_path = os.path.join(input_directory, subfolder_name)
    os.makedirs(subfolder_path, exist_ok=True)

    for item in os.listdir(input_directory):
        item_full_path = os.path.join(input_directory, item)
        # Skip directories (except the destination folder) or any subfolders you don't want to move.
        if os.path.isdir(item_full_path) and item != subfolder_name:
            continue
        # Skip the original TXT files.
        if item_full_path in original_txt_files:
            continue
        # Move every other file.
        if os.path.isfile(item_full_path):
            destination = os.path.join(subfolder_path, os.path.basename(item_full_path))
            # Overwrite the file if it already exists.
            if os.path.exists(destination):
                os.remove(destination)
            shutil.move(item_full_path, destination)

# -------------------------------
# Main 5-iteration loop
# -------------------------------
# Store the full paths to the original .txt files so we don't move them:
original_txt_files = [
    os.path.join(input_directory, os.path.basename(tf)) 
    for tf in text_files
]

# We will keep appending to this combined CSV file each iteration.
combined_csv_path = os.path.join(
    script_directory, f"{os.path.basename(input_directory)}.csv"
)

for iteration in range(1, 6):
    iteration_suffix = get_ordinal_suffix(iteration)  # e.g. "1st", "2nd", etc.
    print("=" * 60)
    print(f"Starting {iteration_suffix} iteration...")  # <--- changed statement
    print("=" * 60)

    # Track CSV files created this iteration
    iteration_successful_csvs = []
    iteration_success = True

    # Process each text file
    for input_file in text_files:
        print(f"Processing: {input_file}")
        result = process_text_file(
            input_file,
            base_prompts,
            new_delimiter_instruction,
            iteration_successful_csvs
        )
        if not result:
            # If we fail for even one file, treat the entire iteration as failure
            iteration_success = False
            # If you want to stop processing further files, uncomment below:
            # break

    # If this iteration generated any CSV files, append them to the 
    # combined CSV (only write a header if the combined CSV doesn't exist yet).
    if iteration_successful_csvs:
        # Check if the combined CSV already exists
        file_already_exists = os.path.exists(combined_csv_path)

        mode = "a" if file_already_exists else "w"
        with open(combined_csv_path, mode=mode, newline="", encoding="utf-8") as combined_csv:
            writer = csv.writer(combined_csv)
            for i, csv_file in enumerate(iteration_successful_csvs):
                with open(csv_file, mode="r", encoding="utf-8") as f_csv:
                    reader = csv.reader(f_csv)
                    rows = list(reader)

                    # If the combined CSV didn't exist previously and this is 
                    # the first iteration CSV, we include the header.
                    if (not file_already_exists) and i == 0:
                        writer.writerows(rows)  # includes header
                    else:
                        # If we're appending, skip the header row for each CSV.
                        writer.writerows(rows[1:])  

        print(f"[Iteration {iteration_suffix}] Appended to combined CSV: {combined_csv_path}")

    # Decide the subfolder name
    if iteration_success:
        subfolder_name = f"{iteration_suffix}-iteration"
    else:
        subfolder_name = f"{iteration_suffix}-iteration_error"

    print(f"Moving non-txt files to subfolder: {subfolder_name}")
    move_non_txt_files_into_subfolder(input_directory, subfolder_name, original_txt_files)

print("All 5 iterations complete.")