import os
import csv
import sys


def create_corpus_folder(corpus_name):
    """Create a folder for the corpus if it doesn't already exist."""
    if not os.path.exists(corpus_name):
        os.makedirs(corpus_name)
        print(f"Folder '{corpus_name}' created.")
    else:
        print(f"Folder '{corpus_name}' already exists.")


def process_csv(csv_file, corpus_name):
    """Process the CSV file and create text files for each line."""
    try:
        with open(csv_file, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Extract necessary fields
                publication_date = row.get("Publication Date", "unknown_date")
                title = row.get("Title", "No Title").replace("/", "-")  # Replace slashes to avoid file issues
                content = row.get("Content", "")

                # Create the filename and path
                filename = f"{publication_date} - {title}.txt"
                filepath = os.path.join(corpus_name, filename)

                # Write content to the text file
                with open(filepath, mode="w", encoding="utf-8") as text_file:
                    text_file.write(content)
                print(f"File created: {filepath}")

    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' does not exist.")
        sys.exit(1)
    except KeyError as e:
        print(f"Error: Missing expected column in CSV: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python AntConc-formatter.py <csv_file>")
        sys.exit(1)

    # Get the CSV file from arguments
    csv_file = sys.argv[1]

    # Derive the corpus name from the CSV filename
    if not csv_file.endswith(".csv"):
        print("Error: The provided file must be a CSV file.")
        sys.exit(1)

    corpus_name = os.path.splitext(os.path.basename(csv_file))[0]

    # Create the corpus folder
    create_corpus_folder(corpus_name)

    # Process the CSV and create text files
    process_csv(csv_file, corpus_name)

    print("Processing complete. Text files have been created.")