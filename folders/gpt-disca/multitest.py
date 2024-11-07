import sys
import pexpect
import re

# Function to remove control characters (ANSI escape sequences) using the provided regular expression
def remove_control_characters(text):
    # Regular expression to match ANSI escape sequences
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    return ansi_escape.sub('', text)

# Start the gpt.py script
command = f"{sys.executable} gpt.py --model gpt-4o --no_stream GrammarHelper"
child = pexpect.spawn(command, echo=False)

# Set a longer timeout to accommodate longer response times
child.timeout = 120

# Function to send a prompt and capture the output
def send_prompt_and_capture_output(prompt):
    # Send the prompt
    child.sendline(prompt)
    
    # Wait for the complete output after sending the prompt, ending with "Tokens:"
    child.expect(r'Tokens:')
    
    # Capture the output
    response = child.before.decode('utf-8')
    
    return response

# Wait for the initial prompt (">")
child.expect(r'>')

# List of prompts to be sent
prompts = [
    "Can you check the following paragraph, located after the colon, for grammar mistakes, count the number of mistakes, place the number of grammar mistakes between TWO @ symbols even if the number is zero, explain each of the mistakes, and provide a revised paragraph: Several epidermal growth factor receptor (EGFR) gene variants are highly associated with many cancers [ref] including non-small cell lung cancer, which is the second-most common lung cancer type worldwide [ref]. Notably, gefitinib (Iressa) and osimertinib (Tagrisso), well-known anti-cancer drugs, were developed to inhibit EGFR-related cell signaling pathways. Given the clinical importance of EGFR variants, detecting or monitoring these critical variants facilitates the diagnosis of cancers, decision of cancer treatment, and improved prognosis of patients. Therefore, EGFR reference materials (RMs) have been developed in several national metrology institutes and companies. However, commercially available EGFR RMs commonly possess one limitation that RMs consist of genomic DNA (gDNA) or artificially fragmented gDNA. Since liquid biopsies, which detect circulating tumor DNA (ctDNA) from entire cell-free DNA (cfDNA) in patients’ blood draws, become widely used in routine clinical laboratories for screening cancers, EGFR RMs are expected to contain EGFR variants in cfDNA-like forms. As cfDNA is derived from nucleosomal DNA (nDNA), this study will suggest nucleosomal DNA (nDNA) for EGFR RMs to reflect patients’ liquid biopsy results.",
    "Next, please categorize those errors according to the following types of errors, even if the number of errors for a certain type is zero: Preposition errors (for these errors the delimiter is '!', for example !0!, !1!, etc), Morphology errors (for these errors the delimiter is '#', for example #0#, #1#, etc), Determiner errors (for these errors the delimiter is '$', for example $0$, $1$, etc), Tense/Aspect errors (for these errors the delimiter is '%', for example %0%, %1%, etc), Agreement errors (for these errors the delimiter is '^', for example ^0^, ^1^, etc), Syntax errors (for these errors the delimiter is '&', for example &0&, &1&, etc), Punctuation errors (for these errors the delimiter is '£', for example £0£, £1£, etc), Spelling errors (for these errors the delimiter is '~', for example ~0~, ~1~, etc), Unidiomatic errors (for these errors the delimiter is '+', for example +0+, +1+, etc), Multiple errors (for these errors the delimiter is '=', for example =0=, =1=, etc), and Miscellaneous errors (for these errors the delimiter is '₩', for example ₩0₩, ₩1₩, etc). Make sure that the sum total number matches the sum of the individual error types, using @ as the delimiter, as discussed earlier. Start your answer with all error numbers in their delimiters (even if the number of errors for a certain error type is 0), each separated by a space on the first line.",
    "Multiply the number of errors by 3."
]

# Iterate over each prompt, send it, and capture the output
for i, prompt in enumerate(prompts, start=1):
    response = send_prompt_and_capture_output(prompt)
    
    # Save the raw response to a file
    output_filename = f'output{i}.txt'
    with open(output_filename, 'w') as file:
        file.write(response)
    
    print(f"Saved raw output to {output_filename}")

# Post-process each output file to extract the relevant content
for i in range(1, len(prompts) + 1):
    input_filename = f'output{i}.txt'
    output_filename = f'finaloutput{i}.txt'
    
    with open(input_filename, 'r') as file:
        content = file.read()
        
        # Find the last occurrences of the specific strings
        start_index_1 = content.rfind("[1A[2K[32m")
        start_index_2 = content.rfind("[1A[2K[3;32m")
        start_index_3 = content.rfind("[J[?7h")
        start_index = max(start_index_1, start_index_3)
        end_index_1 = content.rfind("[?25h")
        end_index_2 = content.rfind("[0m[2m")
        end_index = max(end_index_1, end_index_2)
        
        if start_index != -1 and end_index != -1:
            # Extract the content between the two strings
            final_content = content[start_index + len("[1A[2K[32m"):end_index].strip()
            
            # Remove specific control sequences
            final_content = final_content.replace("[0m", "").replace("[32m", "")
            final_content = final_content.replace("[1;33m", "").replace("[1;32m", "")
            final_content = final_content.replace("[3;32m1", "").replace("[1;32m", "")
            
            # Remove all remaining ANSI control sequences using the new regular expression
            final_content = remove_control_characters(final_content)
            
            with open(output_filename, 'w') as final_file:
                final_file.write(final_content)
            
            print(f"Saved cleaned output to {output_filename}")
        else:
            print(f"Could not find the specified markers in {input_filename}")

# End the interactive session
child.sendline('exit')
child.close()