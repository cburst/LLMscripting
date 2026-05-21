import sys
import os
import subprocess
from collections import Counter
import csv

import re
import unicodedata


def clean_text(text):
    text = unicodedata.normalize("NFKC", text)

    quote_variants = [
        "‘", "’", "‚", "‛",
        "“", "”", "„", "‟",
        "`", "´", "′", "″"
    ]

    for char in quote_variants:
        text = text.replace(char, "'")

    text = re.sub(r"[^A-Za-z0-9 !?\.,\-']", "", text)
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

    # 4-6. Read TSV safely and create one text file per row after header
    with open(tsv_file, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")

        next(reader, None)  # skip header

        for row in reader:
            if len(row) > 1 and row[1].strip():
                filename = row[0].strip()
                text_content = clean_text(row[1])

                if filename:
                    txt_file_path = os.path.join(directory_path, f"{filename}.txt")

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