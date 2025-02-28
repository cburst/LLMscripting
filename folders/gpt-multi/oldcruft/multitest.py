import sys
import subprocess
import re
import os

# Function to remove control characters (ANSI escape sequences) using the provided regular expression
def remove_control_characters(text):
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    return ansi_escape.sub('', text)

# Start the gpt.py script using subprocess
def start_gpt_session():
    # Set environment variables to avoid issues with terminal size expectations
    env = os.environ.copy()
    env['COLUMNS'] = '80'  # You can adjust this as needed
    env['LINES'] = '24'

    command = [sys.executable, "gpt.py", "--model", "gpt-4o", "--no_stream", "GrammarHelper"]
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env  # Pass the environment variables to the subprocess
    )
    return process

# Function to send a prompt and capture the output
def send_prompt_and_capture_output(process, prompt):
    # Send the prompt
    process.stdin.write(prompt + "\n")
    process.stdin.flush()

    response = ''
    try:
        while True:
            output = process.stdout.readline()
            if output:
                response += output
            # End the loop when we see "Tokens:" in the output
            if "Tokens:" in output:
                break
    except Exception as e:
        print(f"Error: {e}")

    return response

# Function to clean the output by removing everything BEFORE and including lastline, and AFTER "Tokens:"
def post_process_output(content):
    lines = content.splitlines()

    # Initialize variables to track the secondlastline and lastline
    secondlastline_index = -1

    # Iterate backwards through the lines to find the last single-letter line
    for i in range(len(lines) - 1, -1, -1):
        # Check if the line only contains a single letter (ignoring spaces)
        if len(lines[i].strip()) == 1:
            secondlastline_index = i
            break

    # If we found such a line and it's not the last line, we proceed
    if secondlastline_index != -1 and secondlastline_index < len(lines) - 1:
        lastline_index = secondlastline_index + 1

        # Remove all content before and including lastline
        cleaned_content = '\n'.join(lines[lastline_index + 1:])

        # Remove all content after and including "Tokens:"
        tokens_index = cleaned_content.find("Tokens:")
        if tokens_index != -1:
            cleaned_content = cleaned_content[:tokens_index].strip()

        # Clean ANSI escape sequences and other control characters
        cleaned_content = remove_control_characters(cleaned_content)

        return cleaned_content

    # If no single-letter line was found, return the content unchanged
    return content

# Start the gpt.py process
gpt_process = start_gpt_session()

# List of prompts to be sent
prompts = [
    "Can you check the following paragraph, located after the colon, for grammar mistakes, count the number of mistakes, place the number of grammar mistakes between TWO @ symbols even if the number is zero, explain each of the mistakes, and provide a revised paragraph: Several epidermal growth factor receptor (EGFR) gene variants are highly associated with many cancers [ref] including non-small cell lung cancer, which is the second-most common lung cancer type worldwide [ref]. Notably, gefitinib (Iressa) and osimertinib (Tagrisso), well-known anti-cancer drugs, were developed to inhibit EGFR-related cell signaling pathways. Given the clinical importance of EGFR variants, detecting or monitoring these critical variants facilitates the diagnosis of cancers, decision of cancer treatment, and improved prognosis of patients. Therefore, EGFR reference materials (RMs) have been developed in several national metrology institutes and companies. However, commercially available EGFR RMs commonly possess one limitation that RMs consist of genomic DNA (gDNA) or artificially fragmented gDNA. Since liquid biopsies, which detect circulating tumor DNA (ctDNA) from entire cell-free DNA (cfDNA) in patients’ blood draws, become widely used in routine clinical laboratories for screening cancers, EGFR RMs are expected to contain EGFR variants in cfDNA-like forms. As cfDNA is derived from nucleosomal DNA (nDNA), this study will suggest nucleosomal DNA (nDNA) for EGFR RMs to reflect patients’ liquid biopsy results.",
    "Next, please categorize those errors according to the following types of errors, even if the number of errors for a certain type is zero: Preposition errors (for these errors the delimiter is '!', for example !0!, !1!, etc), Morphology errors (for these errors the delimiter is '#', for example #0#, #1#, etc), Determiner errors (for these errors the delimiter is '$', for example $0$, $1$, etc), Tense/Aspect errors (for these errors the delimiter is '%', for example %0%, %1%, etc), Agreement errors (for these errors the delimiter is '^', for example ^0^, ^1^, etc), Syntax errors (for these errors the delimiter is '&', for example &0&, &1&, etc), Punctuation errors (for these errors the delimiter is '£', for example £0£, £1£, etc), Spelling errors (for these errors the delimiter is '~', for example ~0~, ~1~, etc), Unidiomatic errors (for these errors the delimiter is '+', for example +0+, +1+, etc), Multiple errors (for these errors the delimiter is '=', for example =0=, =1=, etc), and Miscellaneous errors (for these errors the delimiter is '₩', for example ₩0₩, ₩1₩, etc). Make sure that the sum total number matches the sum of the individual error types, using @ as the delimiter, as discussed earlier. Start your answer with all error numbers in their delimiters (even if the number of errors for a certain error type is 0), each separated by a space on the first line.",
    "Are you sure there are no other errors? Please carefully double check. Start your answer with all updated error numbers in their delimiters (even if the number of errors for a certain error type is 0), each separated by a space on the first line."
]

# Iterate over each prompt, send it, and capture the output
for i, prompt in enumerate(prompts, start=1):
    response = send_prompt_and_capture_output(gpt_process, prompt)

    # Save the raw response to a file
    output_filename = f'output{i}.txt'
    with open(output_filename, 'w') as file:
        file.write(response)

    print(f"Saved raw output to {output_filename}")

    # Post-process each output file to extract the relevant content
    processed_output = post_process_output(response)

    # Save the processed output to another file
    output_filename_processed = f'finaloutput{i}.txt'
    with open(output_filename_processed, 'w') as file:
        file.write(processed_output)

    print(f"Saved cleaned output to {output_filename_processed}")

# End the interactive session
gpt_process.stdin.write('exit\n')
gpt_process.stdin.flush()
gpt_process.terminate()