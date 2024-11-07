import re
import csv
import sys
import os

def clean_specific_string(text):
    # Remove the specific string "between two @ symbols" case-insensitively
    return re.sub(r"between two @ symbols", "", text, flags=re.IGNORECASE)

def filter_csv(file_path):
    # Pattern to match strings with one or more occurrences of one, two, or three digits between @ symbols (e.g., @1@, @@1@@, @999@, or @@999@@) and no other @ symbols
    pattern = re.compile(r'([^@]*@{1,2}\d{1,3}@{1,2}[^@]*)+')
    
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
            # Remove the specific string "between two @ symbols" from each cell
            cleaned_row = [clean_specific_string(cell) for cell in row]
            # Filter rows that match the regex pattern
            if any(pattern.search(cell) for cell in cleaned_row):
                lines.append(cleaned_row)
            else:
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