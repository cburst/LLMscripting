#!/bin/bash

# Check if the directory argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 directory_path"
    exit 1
fi

# Directory containing the files to check
file_directory="$1"

# Construct the CSV file path
csv_file="${file_directory}.CSV"

# Working directory where files are moved
working_directory="${file_directory}/workingdirectory"

# Create working directory if it doesn't exist
mkdir -p "$working_directory"

# Function to count occurrences in CSV
count_occurrences() {
    local file="${1%.*}" # Remove the extension from the filename
    grep -c "$file" "$csv_file"
}

# Function to get file size
get_file_size() {
    local file="$1"
    stat -f%z "$file" # %z gives the size of the file in bytes
}

# Function to process text files and update CSV
process_files() {
    for i in "$working_directory"/*.txt; do
        if [ -f "$i" ] && [ "$(get_file_size "$i")" -gt 5 ]; then  # Check if it's a file and size is greater than 5 bytes
            output="$(python3 gpt.py -p "`cat "$i"`" --model "gpt-4o" )"
            output_escaped="${output//\"/\"\"}"
            echo "\"$(basename "$i")\",\"$output_escaped\"" >> "$csv_file"
        fi
    done
}

# Main loop
while true; do
    all_files_met_condition=true

    # Loop through each file in the directory
    for file in "$file_directory"/*; do
        if [ -f "$file" ] && [ "$(get_file_size "$file")" -gt 5 ]; then  # Check if it's a file and size is greater than 5 bytes
            filename=$(basename "$file")

            # Count how many times this file appears in the CSV
            count=$(count_occurrences "$filename")

            echo "File: $filename, Count: $count" # Debugging line

            if [ "$count" -lt 5 ]; then
                all_files_met_condition=false
                # Copy file to working directory if not already there
                if [ ! -f "${working_directory}/${filename}" ]; then
                    cp "$file" "${working_directory}/"
                fi
            else
                # Delete file from working directory if it's there
                if [ -f "${working_directory}/${filename}" ]; then
                    rm "${working_directory}/${filename}"
                fi
            fi
        fi
    done

    # Run the file processing only if any file needs processing
    if [ "$all_files_met_condition" = false ]; then
        process_files
    fi

    # Check if the condition is met for all files
    if [ "$all_files_met_condition" = true ]; then
        echo "All files have appeared 5 times in the CSV."
        break
    fi

    # Optional: Add a delay to avoid rapid, continuous execution
    sleep 5
done
