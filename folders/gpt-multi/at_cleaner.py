import re
import csv
import sys
import os

def remove_non_visible_chars(text):
    # Remove non-visible characters while preserving visible symbols like the British pound (£), Euro (€), and Won (₩)
    return re.sub(r'[^\x20-\x7E£€₩]', '', text)

def check_for_at_in_csv(file_path):
    pattern = re.compile(r'@')  # Pattern to detect any @ symbol
    
    at_violations = 0
    total_lines = 0
    removed_lines = 0

    with open(file_path, mode='r', encoding='utf-8', newline='') as file:
        reader = csv.reader(file)
        lines = []
        for row in reader:
            total_lines += 1
            if len(row) > 1:  # Ensure the row has at least two columns
                cleaned_text = remove_non_visible_chars(row[1])  # Clean the text in the second column
                if pattern.search(cleaned_text):  # Check only the second column for any @ symbol
                    lines.append(row)
                else:
                    at_violations += 1
                    removed_lines += 1
            else:
                at_violations += 1
                removed_lines += 1
    
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(lines)
    
    print(f"Total lines processed: {total_lines}")
    print(f"Total lines removed: {removed_lines}")
    
    # Only calculate percentage if total_lines > 0 to avoid division by zero
    if total_lines > 0:
        print(f"Percent of lines removed: {removed_lines / total_lines * 100:.2f}%")
    else:
        print("No lines to process.")
    
    print(f"@ condition violations: {at_violations}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py file.csv")
    else:
        file_path = sys.argv[1]
        check_for_at_in_csv(file_path)