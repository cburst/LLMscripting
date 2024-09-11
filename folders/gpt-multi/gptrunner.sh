#!/bin/bash

# Get the directory where the script.sh is located
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Step 1: Receive directory name as argument
d=$1

# Check if the directory name is provided
if [ -z "$d" ]; then
    echo "Error: No directory name provided."
    exit 1
fi

# Step 2: Look for the tsv file
tsv_file="${d}prompts.tsv"

if [ ! -f "$tsv_file" ]; then
    echo "Error: tsv file '$tsv_file' not found."
    exit 1
fi

# Step 3: Copy the tsv file into the directory
if [ ! -d "$d" ]; then
    mkdir "$d"
fi

cp "$tsv_file" "$d/"

# Step 4: Run the AWK command on the tsv file
cd "$d"
awk -F, 'BEGIN {FS="\t"}; {print $2 > ($1 ".txt")}' "$tsv_file"
rm "$tsv_file"
cd ..
touch "${d}.csv"
# Step 5: Run fiver.sh with the directory name as argument
python3 fiver.py "$d"


# Step 6: Run cleaner.py on the csv file
python3 cleaner.py "${d}.csv"

# Step 7: Run fiver.sh with the directory name as argument
python3 fiver.py "$d"


# Step 8: Run cleaner.py on the csv file
python3 cleaner.py "${d}.csv"

echo "Operation completed."
