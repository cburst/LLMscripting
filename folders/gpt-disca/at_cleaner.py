import re
import csv
import sys
import os

def remove_non_visible_chars(text):
    # Remove non-visible characters while keeping visible symbols intact
    return re.sub(r'[^\x20-\x7E]', '', text)

def check_for_comma_space_format(file_path):
    # Pattern to detect any space not directly after a comma (", ")
    invalid_space_pattern = re.compile(r'[^,]\s')
    
    total_lines = 0
    removed_lines = 0

    with open(file_path, mode='r', encoding='utf-8', newline='') as file:
        reader = csv.reader(file)
        lines = []
        for row in reader:
            total_lines += 1
            if len(row) > 1:  # Ensure the row has at least two columns
                first_col = remove_non_visible_chars(row[0])
                second_col = remove_non_visible_chars(row[1])
                
                # Check if the first and second columns contain spaces not directly after a comma
                if not invalid_space_pattern.search(first_col) and not invalid_space_pattern.search(second_col):
                    lines.append(row)  # Keep rows where space only appears after commas
                else:
                    removed_lines += 1  # Count lines with invalid spaces as removed
            else:
                removed_lines += 1  # Count rows with fewer than two columns as removed
    
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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py file.csv")
    else:
        file_path = sys.argv[1]
        check_for_comma_space_format(file_path)