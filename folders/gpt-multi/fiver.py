import subprocess
import time
import csv
import glob
import sys
import os
import re
import shutil

# -------------------------------
# Helper: Safe move with retries.
# -------------------------------
def safe_move(src, dst, retries=10, delay=0.5):
    """Try to move src to dst, retrying if a PermissionError occurs."""
    for attempt in range(retries):
        try:
            shutil.move(src, dst)
            print(f"Moved file on attempt {attempt + 1}: {src} -> {dst}")
            return
        except PermissionError as e:
            print(f"Attempt {attempt+1}: PermissionError encountered moving {src}. Retrying in {delay} seconds...")
            time.sleep(delay)
    # If still failing after retries, raise the exception.
    raise PermissionError(f"Unable to move {src} to {dst} after {retries} retries")

# -------------------------------
# Platform-specific GPT process spawning
# -------------------------------
if os.name == "nt":
    try:
        import winpty
    except ImportError:
        print("Error: winpty is not installed. Please install it with: pip install winpty")
        sys.exit(1)

    class ProcessWrapper:
        """
        A minimal wrapper to mimic the stdin/stdout interface used in our script.
        This wraps the winpty.PTY object.
        """
        def __init__(self, pty):
            self.pty = pty

        @property
        def stdin(self):
            return self

        @property
        def stdout(self):
            return self

        def write(self, data):
            # Write data to the PTY.
            self.pty.write(data)

        def flush(self):
            # No flush needed for winpty.
            pass

        def readline(self):
            # Read characters until a newline is encountered.
            line = ""
            while True:
                ch = self.pty.read(1)
                if not ch:
                    break
                line += ch
                if ch == "\n":
                    break
            return line

        def kill(self):
            # Attempt to kill/close the PTY, if available.
            try:
                self.pty.kill()  # If a kill() method exists
            except AttributeError:
                pass

        def communicate(self):
            # In our case, we simply pause a moment to let the process wrap up.
            time.sleep(1)

    def spawn_gpt():
        """
        Spawn the GPT process using winpty on Windows.
        Returns a ProcessWrapper that mimics subprocess.Popen.
        """
        pty_instance = winpty.PTY(cols=80, rows=24)
        # Use a full command string. Adjust "gpt.exe" if needed.
        pty_instance.spawn("gpt.exe --model gpt-4o GrammarHelper")
        return ProcessWrapper(pty_instance)
else:
    def spawn_gpt():
        """
        Spawn the GPT process using subprocess.Popen on non-Windows systems.
        """
        return subprocess.Popen(
            ["gpt", "--model", "gpt-4o", "GrammarHelper"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

# -------------------------------
# End platform-specific section
# -------------------------------

def get_ordinal_suffix(n):
    """
    Return the ordinal suffix for an integer n: '1st', '2nd', '3rd', etc.
    """
    if 11 <= (n % 100) <= 13:
        return f"{n}th"
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
        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
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

    with open(log_file_path, "r", encoding="utf-8", errors="replace") as log_file:
        log_data = log_file.read()

        # Extract responses using assistant messages.
        matches = re.findall(
            r"gptcli-session - INFO - assistant:.*?<<start>>(.*?)<<end>>",
            log_data, 
            re.DOTALL
        )

        if len(matches) < num_prompts:
            print(f"Error: Missing responses for {filename}. Expected {num_prompts}, but got {len(matches)}.")
            return False

        # Preserve line breaks inside responses.
        responses = [resp.strip() for resp in matches]

    csv_file = os.path.join(input_directory, f"{filename}.csv")
    header = ["filename"] + [f"prompt{str(i+1).zfill(2)}" for i in range(num_prompts)]

    with open(csv_file, mode="w", newline="", encoding="utf-8") as f_csv:
        writer = csv.writer(f_csv, quoting=csv.QUOTE_ALL)
        writer.writerow(header)  # Write header.
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
        # Move old log file instead of deleting it.
        if os.path.exists(log_file_path):
            error_logfile = os.path.join(
                input_directory, f"gptcli_{filename}_error{failure_counter + 1}.log"
            )
            safe_move(log_file_path, error_logfile)
            print(f"Saved failed attempt log: {error_logfile}")

        with open(input_file, "r", encoding="utf-8") as f_in:
            file_text = f_in.read().strip()

        # Start a new GPT process for this file using our spawn_gpt() helper.
        process = spawn_gpt()

        # Read the initial prompt from GPT (for Windows, our wrapper provides readline()).
        process.stdout.readline()

        # Send each base prompt.
        for i, base_prompt in enumerate(base_prompts):
            if i == 0:
                full_prompt = f"{new_delimiter_instruction} {base_prompt} {file_text}"
            else:
                full_prompt = f"{new_delimiter_instruction} {base_prompt}"

            full_prompt = full_prompt.replace('"', '')
            process.stdin.write(full_prompt + "\n")
            process.stdin.flush()

            # Wait for the response before sending the next prompt.
            success = wait_for_responses(i + 1)
            if not success:
                print(f"Error: Timeout waiting for response {i + 1} for {filename}. Retrying...")
                failure_counter += 1
                process.kill()
                break  # Restart the GPT process.
        else:
            # If we didn't break early, we got all prompts.
            process.stdin.write(":q\n")
            process.stdin.flush()
            process.communicate()

            # Extract responses and save CSV.
            if extract_responses_and_save(filename, iteration_successful_csvs):
                new_logfile = os.path.join(input_directory, f"gptcli_{filename}.txt")
                safe_move(log_file_path, new_logfile)
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
    into a subdirectory named `subfolder_name`.
    """
    subfolder_path = os.path.join(input_directory, subfolder_name)
    os.makedirs(subfolder_path, exist_ok=True)

    for item in os.listdir(input_directory):
        item_full_path = os.path.join(input_directory, item)
        if os.path.isdir(item_full_path) and item != subfolder_name:
            continue
        if item_full_path in original_txt_files:
            continue
        if os.path.isfile(item_full_path):
            destination = os.path.join(subfolder_path, os.path.basename(item_full_path))
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
    print(f"Starting {iteration_suffix} iteration...")
    print("=" * 60)

    # Track CSV files created this iteration.
    iteration_successful_csvs = []
    iteration_success = True

    # Process each text file.
    for input_file in text_files:
        print(f"Processing: {input_file}")
        result = process_text_file(
            input_file,
            base_prompts,
            new_delimiter_instruction,
            iteration_successful_csvs
        )
        if not result:
            iteration_success = False
            # Optionally, break out of the loop if desired.
            # break

    # If this iteration generated any CSV files, append them to the combined CSV.
    if iteration_successful_csvs:
        file_already_exists = os.path.exists(combined_csv_path)
        mode = "a" if file_already_exists else "w"
        with open(combined_csv_path, mode=mode, newline="", encoding="utf-8") as combined_csv:
            writer = csv.writer(combined_csv)
            for i, csv_file in enumerate(iteration_successful_csvs):
                with open(csv_file, mode="r", encoding="utf-8") as f_csv:
                    reader = csv.reader(f_csv)
                    rows = list(reader)
                    if (not file_already_exists) and i == 0:
                        writer.writerows(rows)  # Write header.
                    else:
                        writer.writerows(rows[1:])  # Skip header for appended files.

        print(f"[Iteration {iteration_suffix}] Appended to combined CSV: {combined_csv_path}")

    # Decide the subfolder name.
    if iteration_success:
        subfolder_name = f"{iteration_suffix}-iteration"
    else:
        subfolder_name = f"{iteration_suffix}-iteration_error"

    print(f"Moving non-txt files to subfolder: {subfolder_name}")
    move_non_txt_files_into_subfolder(input_directory, subfolder_name, original_txt_files)

print("All 5 iterations complete.")