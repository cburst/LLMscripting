import re
import csv
import sys
import os

def remove_non_visible_chars(text):
    # Remove non-visible characters while preserving visible symbols like the British pound (£), Euro (€), and Won (₩)
    return re.sub(r'[^\x20-\x7E£€₩]', '', text)

def check_for_at_in_csv(file_path):
    pattern = re.compile(r'([^@]*@{1,2}\d{1,3}@{1,2}[^@]*)+')
    
    at_violations = 0
    total_lines = 0
    removed_lines = 0

    with open(file_path, mode='r', encoding='utf-8', newline='') as file:
        reader = csv.reader(file)
        lines = []
        for row in reader:
            total_lines += 1
            if len(row) > 3:
                cleaned_text = remove_non_visible_chars(row[3])  # Clean the text in the fourth column
                if pattern.search(cleaned_text):  # Check only the fourth column
                    lines.append(row)
                else:
                    at_violations += 1
                    removed_lines += 1
    
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(lines)
    
    return total_lines, removed_lines, at_violations

def check_for_exclampt_in_csv(file_path):
    pattern = re.compile(r'([^!]*!{1,2}\d{1,3}!{1,2}[^!]*)+')
    
    excl_violations = 0
    total_lines = 0
    removed_lines = 0

    with open(file_path, mode='r', encoding='utf-8', newline='') as file:
        reader = csv.reader(file)
        lines = []
        for row in reader:
            total_lines += 1
            if len(row) > 3:
                cleaned_text = remove_non_visible_chars(row[3])  # Clean the text in the fourth column
                if pattern.search(cleaned_text):  # Check only the fourth column
                    lines.append(row)
                else:
                    excl_violations += 1
                    removed_lines += 1
    
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(lines)
    
    return total_lines, removed_lines, excl_violations

def check_for_britishpound_in_csv(file_path):
    pattern = re.compile(r'£\d{1,3}£')  # Simplified pattern to match £digits£

    britishpound_violations = 0
    total_lines = 0
    removed_lines = 0

    with open(file_path, mode='r', encoding='utf-8', newline='') as file:
        reader = csv.reader(file)
        lines = []
        for row in reader:
            total_lines += 1
            if len(row) > 3:
                cleaned_text = remove_non_visible_chars(row[3])  # Clean the text in the fourth column
                if pattern.search(cleaned_text):  # Check only the fourth column
                    lines.append(row)
                    # print(f"Pattern found: {cleaned_text}")  # Debugging line
                else:
                    britishpound_violations += 1
                    removed_lines += 1
                    # print(f"Violation detected: {cleaned_text}")  # Debugging line
            else:
                britishpound_violations += 1
                removed_lines += 1
                print(f"Violation detected: Empty or insufficient columns")  # Debugging line
    
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(lines)
    
    return total_lines, removed_lines, britishpound_violations

def check_for_euro_in_csv(file_path):
    pattern = re.compile(r'([^€]*€{1,2}\d{1,3}€{1,2}[^€]*)+')
    
    euro_violations = 0
    total_lines = 0
    removed_lines = 0

    with open(file_path, mode='r', encoding='utf-8', newline='') as file:
        reader = csv.reader(file)
        lines = []
        for row in reader:
            total_lines += 1
            if len(row) > 3:
                cleaned_text = remove_non_visible_chars(row[3])  # Clean the text in the fourth column
                if pattern.search(cleaned_text):  # Check only the fourth column
                    lines.append(row)
                else:
                    euro_violations += 1
                    removed_lines += 1
    
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(lines)
    
    return total_lines, removed_lines, euro_violations

def check_for_carrot_in_csv(file_path):
    pattern = re.compile(r'([^^]*\^{1,2}\d{1,3}\^{1,2}[^^]*)+')
    
    carrot_violations = 0
    total_lines = 0
    removed_lines = 0

    with open(file_path, mode='r', encoding='utf-8', newline='') as file:
        reader = csv.reader(file)
        lines = []
        for row in reader:
            total_lines += 1
            if len(row) > 3:
                cleaned_text = remove_non_visible_chars(row[3])  # Clean the text in the fourth column
                if pattern.search(cleaned_text):  # Check only the fourth column
                    lines.append(row)
                else:
                    carrot_violations += 1
                    removed_lines += 1
    
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(lines)
    
    return total_lines, removed_lines, carrot_violations

def check_for_pct_in_csv(file_path):
    pattern = re.compile(r'([^%]*%{1,2}\d{1,3}%{1,2}[^%]*)+')
    
    pct_violations = 0
    total_lines = 0
    removed_lines = 0

    with open(file_path, mode='r', encoding='utf-8', newline='') as file:
        reader = csv.reader(file)
        lines = []
        for row in reader:
            total_lines += 1
            if len(row) > 3:
                cleaned_text = remove_non_visible_chars(row[3])  # Clean the text in the fourth column
                if pattern.search(cleaned_text):  # Check only the fourth column
                    lines.append(row)
                else:
                    pct_violations += 1
                    removed_lines += 1
    
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(lines)
    
    return total_lines, removed_lines, pct_violations

def check_for_amp_in_csv(file_path):
    pattern = re.compile(r'([^&]*&{1,2}\d{1,3}&{1,2}[^&]*)+')
    
    amp_violations = 0
    total_lines = 0
    removed_lines = 0

    with open(file_path, mode='r', encoding='utf-8', newline='') as file:
        reader = csv.reader(file)
        lines = []
        for row in reader:
            total_lines += 1
            if len(row) > 3:
                cleaned_text = remove_non_visible_chars(row[3])  # Clean the text in the fourth column
                if pattern.search(cleaned_text):  # Check only the fourth column
                    lines.append(row)
                else:
                    amp_violations += 1
                    removed_lines += 1
    
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(lines)
    
    return total_lines, removed_lines, amp_violations

def check_for_tilda_in_csv(file_path):
    pattern = re.compile(r'([^~]*~{1,2}\d{1,3}~{1,2}[^~]*)+')
    
    tilda_violations = 0
    total_lines = 0
    removed_lines = 0

    with open(file_path, mode='r', encoding='utf-8', newline='') as file:
        reader = csv.reader(file)
        lines = []
        for row in reader:
            total_lines += 1
            if len(row) > 3:
                cleaned_text = remove_non_visible_chars(row[3])  # Clean the text in the fourth column
                if pattern.search(cleaned_text):  # Check only the fourth column
                    lines.append(row)
                else:
                    tilda_violations += 1
                    removed_lines += 1
    
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(lines)
    
    return total_lines, removed_lines, tilda_violations

def check_for_plus_in_csv(file_path):
    pattern = re.compile(r'([^+]*\+{1,2}\d{1,3}\+{1,2}[^+]*)+')
    
    plus_violations = 0
    total_lines = 0
    removed_lines = 0

    with open(file_path, mode='r', encoding='utf-8', newline='') as file:
        reader = csv.reader(file)
        lines = []
        for row in reader:
            total_lines += 1
            if len(row) > 3:
                cleaned_text = remove_non_visible_chars(row[3])  # Clean the text in the fourth column
                if pattern.search(cleaned_text):  # Check only the fourth column
                    lines.append(row)
                else:
                    plus_violations += 1
                    removed_lines += 1
    
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(lines)
    
    return total_lines, removed_lines, plus_violations

def check_for_eqlsgn_in_csv(file_path):
    pattern = re.compile(r'([^=]*={1,2}\d{1,3}={1,2}[^=]*)+')
    
    eqlsgn_violations = 0
    total_lines = 0
    removed_lines = 0

    with open(file_path, mode='r', encoding='utf-8', newline='') as file:
        reader = csv.reader(file)
        lines = []
        for row in reader:
            total_lines += 1
            if len(row) > 3:
                cleaned_text = remove_non_visible_chars(row[3])  # Clean the text in the fourth column
                if pattern.search(cleaned_text):  # Check only the fourth column
                    lines.append(row)
                else:
                    eqlsgn_violations += 1
                    removed_lines += 1
    
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(lines)
    
    return total_lines, removed_lines, eqlsgn_violations

def check_for_krw_in_csv(file_path):
    pattern = re.compile(r'([^₩]*₩{1,2}\d{1,3}₩{1,2}[^₩]*)+')
    
    krw_violations = 0
    total_lines = 0
    removed_lines = 0

    with open(file_path, mode='r', encoding='utf-8', newline='') as file:
        reader = csv.reader(file)
        lines = []
        for row in reader:
            total_lines += 1
            if len(row) > 3:
                cleaned_text = remove_non_visible_chars(row[3])  # Clean the text in the fourth column
                if pattern.search(cleaned_text):  # Check only the fourth column
                    lines.append(row)
                else:
                    krw_violations += 1
                    removed_lines += 1
    
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(lines)
    
    return total_lines, removed_lines, krw_violations

def print_results(file_path, total_lines, removed_lines, at_violations, excl_violations, britishpound_violations, euro_violations, carrot_violations, pct_violations, amp_violations, tilda_violations, plus_violations, eqlsgn_violations, krw_violations):
    print(f"Cleaning completed for: {os.path.abspath(file_path)}")
    print(f"Total lines processed: {total_lines}")
    print(f"Total lines removed: {removed_lines}")
    
    # Only calculate percentage if total_lines > 0 to avoid division by zero
    if total_lines > 0:
        print(f"Percent of lines removed: {removed_lines / total_lines * 100:.2f}%")
    else:
        print("No lines to process.")
    
    print(f"@ condition violations: {at_violations}")
    print(f"! condition violations: {excl_violations}")
    print(f"£ condition violations: {britishpound_violations}")
    print(f"€ condition violations: {euro_violations}")
    print(f"^ condition violations: {carrot_violations}")
    print(f"% condition violations: {pct_violations}")
    print(f"& condition violations: {amp_violations}")
    print(f"~ condition violations: {tilda_violations}")
    print(f"+ condition violations: {plus_violations}")
    print(f"= condition violations: {eqlsgn_violations}")
    print(f"₩ condition violations: {krw_violations}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py file.csv")
    else:
        file_path = sys.argv[1]
        
        total_lines_at, removed_lines_at, at_violations = check_for_at_in_csv(file_path)
        total_lines_excl, removed_lines_excl, excl_violations = check_for_exclampt_in_csv(file_path)
        total_lines_britishpound, removed_lines_britishpound, britishpound_violations = check_for_britishpound_in_csv(file_path)
        total_lines_euro, removed_lines_euro, euro_violations = check_for_euro_in_csv(file_path)
        total_lines_carrot, removed_lines_carrot, carrot_violations = check_for_carrot_in_csv(file_path)
        total_lines_pct, removed_lines_pct, pct_violations = check_for_pct_in_csv(file_path)
        total_lines_amp, removed_lines_amp, amp_violations = check_for_amp_in_csv(file_path)
        total_lines_tilda, removed_lines_tilda, tilda_violations = check_for_tilda_in_csv(file_path)
        total_lines_plus, removed_lines_plus, plus_violations = check_for_plus_in_csv(file_path)
        total_lines_eqlsgn, removed_lines_eqlsgn, eqlsgn_violations = check_for_eqlsgn_in_csv(file_path)
        total_lines_krw, removed_lines_krw, krw_violations = check_for_krw_in_csv(file_path)
        
        total_lines = total_lines_at
        removed_lines = removed_lines_at + removed_lines_excl + removed_lines_britishpound + removed_lines_euro + removed_lines_carrot + removed_lines_pct + removed_lines_amp + removed_lines_tilda + removed_lines_plus + removed_lines_eqlsgn + removed_lines_krw

        print_results(file_path, total_lines, removed_lines, at_violations, excl_violations, britishpound_violations, euro_violations, carrot_violations, pct_violations, amp_violations, tilda_violations, plus_violations, eqlsgn_violations, krw_violations)