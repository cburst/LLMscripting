# LLMscripting
This is a series of Python scripts for zero-shot and chain-of-though LLM scripting.

Windows Installation
Click 'Releases' on the right and download LLMscripting-WinInstaller.exe
Follow the installation instructions on the releases page.

Mac Installation 
Click 'Releases' on the right and download LLMscripting-MacInstaller.zip
Follow the installation instructions on the releases page.

Usage Instructions
For zero-shot scripting (a series of single LLM prompts)
Place a TSV file containing two columns in the input-files folder, with a filename like yourtexthere-prompts.tsv
The first column should have an identifier (like a student number), and the second column should have the prompts (like 'Please check text after the colon for grammar errors: STUDENT TEXT')
Click the desktop shortcut for LLM Scripting
Type the following command on Windows: python GPT.py yourtexthere-
Type the following command on Mac: python3 GPT.py yourtexthere-

For chain-of-thought scripting (a series of multiple related LLM prompts)
Place a TSV file containing two columns in the input-files folder, with a filename like yourtexthere-raw.tsv
The first column should have an identifier (like a student number), and the second column should have the text (like 'STUDENT TEXT')
To adjust the prompts, edit the prompt text in folders/fiver.py
Click the desktop shortcut for LLM Scripting
Type the following command on Windows: python GPTmulti.py yourtexthere-
Type the following command on Mac: python3 GPTmulti.py yourtexthere-
