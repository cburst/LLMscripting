import sys
import os
import subprocess
from collections import Counter
import csv

import re
import unicodedata


def clean_text(text):
    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)

    # Convert quote/apostrophe variants to plain apostrophe
    quote_variants = [
        "‘", "’", "‚", "‛",
        "“", "”", "„", "‟",
        "`", "´", "′", "″"
    ]

    for char in quote_variants:
        text = text.replace(char, "'")

    # Remove all line breaks and tabs
    text = text.replace("\r", " ")
    text = text.replace("\n", " ")
    text = text.replace("\t", " ")

    # Keep only:
    # letters, numbers, spaces, and ! ? . , - '
    text = re.sub(r"[^A-Za-z0-9 !?\.,\-']", "", text)

    # Collapse repeated whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def main():
    # 1. Receive directory name as argument
    if len(sys.argv) < 2:
        print("Usage: python simplified_script.py <directory_name>")
        sys.exit(1)

    directory_name = sys.argv[1].strip()

    # Directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 2. Check for TSV file
    tsv_file = os.path.join(script_dir, f"{directory_name}raw.tsv")

    if not os.path.isfile(tsv_file):
        print(f"Error: TSV file '{tsv_file}' not found.")
        sys.exit(1)

    # 3. Create output directory
    directory_path = os.path.join(script_dir, directory_name)

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # 4-6. Read TSV and create one text file per row
    with open(tsv_file, "r", encoding="utf-8") as f:

        # Skip header
        next(f)

        for line in f:

            line = line.rstrip("\r\n")

            if "\t" not in line:
                continue

            filename, text_content = line.split("\t", 1)

            filename = filename.strip()

            if not filename:
                continue

            text_content = clean_text(text_content)

            txt_file_path = os.path.join(
                directory_path,
                f"{filename}.txt"
            )

            with open(txt_file_path, "w", encoding="utf-8") as txt_file:
                txt_file.write(text_content)

    # 7. Delete the TSV file now that splitting is done
    if os.path.isfile(tsv_file):
        os.remove(tsv_file)
        print(f"Deleted TSV file: {tsv_file}")

    # 8. Check for a file named [directory_name].csv; if it exists, remove .txt files
    #    in [directory_name] for any first-column value that appears >= 5 times.
    csv_path = os.path.join(script_dir, f"{directory_name}.csv")
    if os.path.isfile(csv_path):
        print(f"Checking '{csv_path}' for values that appear 5 or more times...")
        counts = Counter()
        with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # Skip CSV header
            for row in reader:
                if row and row[0].strip():
                    counts[row[0].strip()] += 1

        # For each key in counts, if it appears >= 5 times, delete the .txt file
        for key, count in counts.items():
            if count >= 5:
                text_file = os.path.join(directory_path, f"{key}.txt")
                if os.path.isfile(text_file):
                    os.remove(text_file)
                    print(f"Deleted file: {text_file}")
    else:
        print(f"No CSV file named '{directory_name}.csv' found. Skipping that step.")

    # 9. Run fiver.py with [directory_name] as an argument
    fiver_script = os.path.join(script_dir, "fiver.py")
    if os.path.isfile(fiver_script):
        subprocess.run([sys.executable, fiver_script, directory_path], check=True)
    else:
        print(f"Warning: 'fiver.py' not found in {script_dir}. Skipping this step.")

    print("Operation completed successfully.")

if __name__ == "__main__":
    main()