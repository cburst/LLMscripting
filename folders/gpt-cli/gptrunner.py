import os
import shutil
import subprocess
import sys

def cleanup(directory, tsv_file):
    """Delete the specified directory and TSV file."""
    try:
        if os.path.exists(directory):
            shutil.rmtree(directory)
        if os.path.exists(tsv_file):
            os.remove(tsv_file)
    except Exception as e:
        print(f"Error during cleanup: {e}")

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Step 1: Receive directory name as argument
if len(sys.argv) < 2:
    print("Error: No directory name provided.")
    sys.exit(1)

d = sys.argv[1]

# Assuming the TSV file is in the same directory as the script and named appropriately
tsv_file = os.path.join(script_dir, f"{d}prompts.tsv")

# Check if the file exists
if not os.path.isfile(tsv_file):
    print(f"Error: TSV file '{tsv_file}' not found.")
    sys.exit(1)

# Step 3: Ensure the directory exists
directory_path = os.path.join(script_dir, d)
if not os.path.exists(directory_path):
    os.makedirs(directory_path)

# Copy the TSV file to the target directory
target_tsv_file = os.path.join(directory_path, f"{d}prompts.tsv")
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
        file_size = os.path.getsize(file_path)  # Get file size before removing
        os.remove(file_path)

# Create an empty CSV file in the script directory (not the target directory)
csv_file = os.path.join(script_dir, f"{d}.csv")
open(csv_file, 'a').close()

# Steps 5 and 6: Run fiver.py and cleaner.py on the csv file twice
def run_python_script(script, argument):
    script_path = os.path.join(script_dir, script)  # Use script_dir to build the full path
    subprocess.run([sys.executable, script_path, argument], check=True)  # Use sys.executable

# Ensure the CSV file exists before running the scripts
if os.path.isfile(csv_file):
    run_python_script('fiver.py', directory_path)  # Run fiver.py with directory_path argument
    run_python_script('cleaner.py', csv_file)      # Run cleaner.py with csv_file argument
    run_python_script('fiver.py', directory_path)  # Repeat as needed
    run_python_script('cleaner.py', csv_file)
    run_python_script('fiver.py', directory_path)
    run_python_script('cleaner.py', csv_file)
    run_python_script('fiver.py', directory_path)
    run_python_script('cleaner.py', csv_file)
else:
    print(f"Error: CSV file '{csv_file}' does not exist.")

# Perform cleanup
cleanup(directory_path, tsv_file)

print("Operation completed.")