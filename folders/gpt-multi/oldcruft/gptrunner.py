import os
import shutil
import subprocess
import sys
import csv
from collections import Counter

def cleanup(directory, tsv_file):
    """Delete the specified directory and TSV file."""
    try:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        if os.path.exists(tsv_file):
            os.remove(tsv_file)
    except Exception as e:
        print(f"Error during cleanup: {e}")

def cleanup_directory_only(directory):
    """Delete the specified directory but retain the TSV file."""
    try:
        if os.path.exists(directory):
            shutil.rmtree(directory)
    except Exception as e:
        print(f"Error during directory-only cleanup: {e}")

def count_filename_occurrences_in_csv(directory, csv_file):
    """Count how many times each filename in the directory appears in the CSV file."""
    filenames_in_directory = {f: 0 for f in os.listdir(directory) if f.endswith(".txt")}
    filename_counts = Counter()

    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:  # Ensure row is not empty
                filename = row[0].strip()  # The filename should be the first column
                filename_counts[filename] += 1

    # Compare counts with directory filenames
    filenames_below_5 = {name: filename_counts.get(name, 0) for name in filenames_in_directory if filename_counts.get(name, 0) < 5}

    # Print filenames that don't appear 5 times
    if filenames_below_5:
        print("These filenames do not appear 5 times:")
        for name, count in filenames_below_5.items():
            print(f"{name}: {count} times")
    else:
        print("All filenames appear at least 5 times in the CSV.")

    return filenames_below_5

def run_python_script(script, argument):
    """Run the specified Python script with an argument."""
    script_path = os.path.join(script_dir, script)  # Use script_dir to build the full path
    subprocess.run([sys.executable, script_path, argument], check=True)  # Use sys.executable

def delete_resource_forks(directory):
    """Delete .DS_Store and other resource forks from the directory."""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == ".DS_Store" or file.startswith("._"):
                file_path = os.path.join(root, file)
                os.remove(file_path)

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Step 1: Receive directory name as argument
if len(sys.argv) < 2:
    print("Error: No directory name provided.")
    sys.exit(1)

d = sys.argv[1]

# Assuming the TSV file is in the same directory as the script and named appropriately
tsv_file = os.path.join(script_dir, f"{d}raw.tsv")

# Check if the file exists
if not os.path.isfile(tsv_file):
    print(f"Error: TSV file '{tsv_file}' not found.")
    sys.exit(1)

# Step 3: Ensure the directory exists
directory_path = os.path.join(script_dir, d)
if not os.path.exists(directory_path):
    os.makedirs(directory_path)

# Copy the TSV file to the target directory
target_tsv_file = os.path.join(directory_path, f"{d}raw.tsv")
shutil.copy(tsv_file, target_tsv_file)

# Step 4: Filter the TSV file to remove lines with empty second columns
filtered_lines = []
with open(target_tsv_file, 'r', encoding='utf-8') as file:
    for line in file:
        columns = line.split('\t')
        if len(columns) > 1 and columns[1].strip():  # Check if the second column is not empty
            filtered_lines.append(line)

# Write the filtered lines back to the TSV file
with open(target_tsv_file, 'w', encoding='utf-8') as file:
    file.writelines(filtered_lines)

# Process the filtered TSV file (managing files within the target directory)
with open(target_tsv_file, 'r', encoding='utf-8') as file:
    for line in file:
        columns = line.split('\t')
        if len(columns) > 1:
            output_file_path = os.path.join(directory_path, f"{columns[0]}.txt")
            with open(output_file_path, 'a', encoding='utf-8') as output_file:
                output_file.write(columns[1])

# Delete any file named ".txt" without a filename prefix
empty_filename_path = os.path.join(directory_path, ".txt")
if os.path.exists(empty_filename_path):
    os.remove(empty_filename_path)
    print("Deleted file: .txt")

# Delete the TSV file in the target directory after processing
os.remove(target_tsv_file)

# Path to the "Student Number.txt" file in the output directory
student_number_file = os.path.join(directory_path, "Student Number.txt")

# Delete the file called "Student Number.txt" after processing
if os.path.exists(student_number_file):
    os.remove(student_number_file)

# Remove files smaller than 250 bytes in the same directory
for filename in os.listdir(directory_path):
    file_path = os.path.join(directory_path, filename)
    # Check if it's a file and its size is smaller than 250 bytes
    if os.path.isfile(file_path) and os.path.getsize(file_path) < 250:
        os.remove(file_path)

# Delete resource forks (e.g., .DS_Store) from the directory
delete_resource_forks(directory_path)

# Create an empty CSV file in the script directory (not the target directory)
csv_file = os.path.join(script_dir, f"{d}.csv")
open(csv_file, 'a').close()

# Ensure the CSV file exists before running the scripts
if os.path.isfile(csv_file):
    run_count = 0
    max_runs = 5

    while run_count < max_runs:
        # Run cleaner scripts at the start of each loop
        print(f"Running cleaner scripts at the start of run {run_count + 1}")
        run_python_script('at_cleaner.py', csv_file)
        run_python_script('all_cleaner.py', csv_file)

        # Check for filenames that appear less than 5 times
        filenames_below_5 = count_filename_occurrences_in_csv(directory_path, csv_file)

        # If no filenames are below 5, exit the loop
        if not filenames_below_5:
            print("All filenames appear at least 5 times. Exiting.")
            break

        # If there are filenames below 5 occurrences, run the fiver.py script
        print(f"Running fiver.py script due to filenames below 5 occurrences in run {run_count + 1}")
        run_python_script('fiver.py', directory_path)  # Run fiver.py with directory_path argument

        # Re-run cleaner scripts after fiver.py script
        print(f"Re-running cleaner scripts after fiver.py execution in run {run_count + 1}")
        run_python_script('at_cleaner.py', csv_file)
        run_python_script('all_cleaner.py', csv_file)

        # Re-count filenames after cleaners
        filenames_below_5 = count_filename_occurrences_in_csv(directory_path, csv_file)

        run_count += 1  # Increment the run count

    if run_count >= max_runs:
        print("Warning: Maximum number of runs reached. Some filenames may not appear exactly 5 times.")

else:
    print(f"Error: CSV file '{csv_file}' does not exist.")

# Perform final cleanup
cleanup(directory_path, tsv_file)

print("Operation completed.")