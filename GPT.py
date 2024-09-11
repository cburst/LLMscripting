import os
import sys
import shutil
import subprocess

def main():
    # Check if exactly one argument is given
    if len(sys.argv) != 2:
        print("Usage: {} dirname".format(sys.argv[0]))
        sys.exit(1)
    
    dirname = sys.argv[1]
    
    # Define the original directory to return to it later
    original_dir = os.getcwd()
    
    # Construct source and destination paths for TSV file
    source_tsv = os.path.join("input-files", f"{dirname}prompts.tsv")
    dest_tsv = os.path.join("folders", "gpt-cli", f"{dirname}prompts.tsv")
    
    # Check if source TSV file exists
    if not os.path.exists(source_tsv):
        print("Error: TSV file '{}' does not exist.".format(source_tsv))
        sys.exit(1)
    
    # Copy the TSV file to the required directory
    shutil.copy(source_tsv, dest_tsv)
    
    # Change directory to folders/gpt-cli
    os.chdir(os.path.join("folders", "gpt-cli"))
    
    # Check if gptrunner.py exists in the destination directory
    gptrunner_script = os.path.join(os.getcwd(), "gptrunner.py")
    if not os.path.exists(gptrunner_script):
        print("Error: gptrunner.py script not found in the destination directory.")
        sys.exit(1)
    
    # Run the Python script with dirname as the argument
    subprocess.run([sys.executable, "gptrunner.py", dirname])
    
    # Change back to the original directory
    os.chdir(original_dir)
    
    # Construct source and destination paths for CSV file
    source_csv = os.path.join("folders", "gpt-cli", f"{dirname}.csv")
    dest_csv = os.path.join("output-files", f"{dirname}-GPT-processed.csv")
    
    # Check if source CSV file exists
    if not os.path.exists(source_csv):
        print("Error: CSV file '{}' does not exist.".format(source_csv))
        sys.exit(1)
    
    # Copy the CSV file to the desired output location with the new filename
    shutil.copy(source_csv, dest_csv)

if __name__ == "__main__":
    main()
