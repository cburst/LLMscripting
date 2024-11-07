import re
import csv
import sys
import os

def remove_non_visible_chars(text):
    # Remove non-visible characters while keeping visible symbols intact
    return re.sub(r'[^\x20-\x7E]', '', text)

def check_third_column_for_valid_numbers_or_string(file_path):
    # Pattern to allow numbers with a single optional + or - sign and one decimal point
    valid_number_pattern = re.compile(r'^[+-]?\d*\.?\d+$')
    valid_string_pattern = re.compile(r'^analysis process\)\s*[\r\n]*$')  # Pattern to match "analysis process)." followed by a line break
    
    total_lines = 0
    removed_lines = 0

    with open(file_path, mode='r', encoding='utf-8', newline='') as file:
        reader = csv.reader(file)
        lines = []
        for row in reader:
            total_lines += 1
            if len(row) > 2:  # Ensure the row has at least three columns
                third_col = remove_non_visible_chars(row[2])
                
                # Check if the third column matches the valid number pattern or the valid string pattern
                if valid_number_pattern.match(third_col) or valid_string_pattern.match(row[2]):
                    lines.append(row)  # Keep rows where the third column is valid
                else:
                    removed_lines += 1  # Count rows with invalid third column as removed
            else:
                removed_lines += 1  # Count rows with fewer than three columns as removed
    
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
        check_third_column_for_valid_numbers_or_string(file_path)