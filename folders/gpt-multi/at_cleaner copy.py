import csv
import sys
import os
import re

def remove_non_visible_chars(text):
    # Remove all non-visible characters from the text (characters with ASCII values outside 32-126)
    return re.sub(r'[^\x20-\x7E]', '', text)

def is_valid_pattern(text):
    first_at = text.find('@')
    if first_at == -1:
        return False  # No @ symbol found
    
    second_at = text.find('@', first_at + 1)
    if second_at == -1:
        return False  # Only one @ symbol found

    # Check if there are only digits between the two @ symbols
    between_ats = text[first_at + 1:second_at]
    if between_ats.isdigit():
        return True
    
    return False

def filter_csv(file_path):
    at_violations = 0
    total_lines = 0
    removed_lines = 0

    # Open the file with utf-8 encoding to handle Unicode characters consistently across platforms
    with open(file_path, mode='r', encoding='utf-8', newline='') as file:
        reader = csv.reader(file)
        
        # Process and filter rows
        lines = []
        for row in reader:
            total_lines += 1
            if len(row) > 1:  # Ensure the row has at least two columns
                # Clean the second column by removing non-visible characters
                cleaned_text = remove_non_visible_chars(row[1])
                # Check if the cleaned text has a valid @digits@ pattern
                if is_valid_pattern(cleaned_text):
                    row[1] = cleaned_text  # Update the row with cleaned text
                    lines.append(row)
                else:
                    at_violations += 1
                    removed_lines += 1
            else:
                # If the row doesn't have a second column, it's considered a violation
                at_violations += 1
                removed_lines += 1
    
    # Write the filtered rows back to the file with utf-8 encoding
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(lines)
    
    # Print the complete path of the CSV file and a completion message
    print(f"Cleaning completed for: {os.path.abspath(file_path)}")
    print(f"Total lines processed: {total_lines}")
    print(f"Total lines removed: {removed_lines}")
    print(f"Percent of lines removed: {removed_lines / total_lines * 100:.2f}%")
    print(f"@ condition violations: {at_violations}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py file.csv")
    else:
        file_path = sys.argv[1]
        filter_csv(file_path)