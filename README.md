# LLMscripting
This is a series of Python scripts for zero-shot and chain-of-thought LLM scripting.

Windows/Mac Installation

1. Click 'Releases' on the right and download LLMscripting-WinInstaller.exe
2. Follow the installation instructions on the releases page.

Usage Instructions

-For zero-shot scripting (a series of single LLM prompts)

1. Place a TSV file containing two columns in the input-files folder, with a filename like yourtexthere-prompts.tsv
2. The first column should have an identifier (like a student number), and the second column should have the prompts (like 'Please check text after the colon for grammar errors: STUDENT TEXT')
3. Click the desktop shortcut for LLM Scripting
4. Type the following command on Windows: python GPT.py yourtexthere-
4. Type the following command on Mac: python3 GPT.py yourtexthere-

-For chain-of-thought scripting (a series of multiple related LLM prompts)

1. Place a TSV file containing two columns in the input-files folder, with a filename like yourtexthere-raw.tsv
2. The first column should have an identifier (like a student number), and the second column should have the text (like 'STUDENT TEXT')
3. To adjust the prompts, edit the prompt text in folders/fiver.py
4. Click the desktop shortcut for LLM Scripting
5. Type the following command on Windows: python GPTmulti.py yourtexthere-
5. Type the following command on Mac: python3 GPTmulti.py yourtexthere-


Citation:

Rose, R. (2024). Improving grammatical accuracy through instructor, peer, and LLM written corrective feedback. Manuscript in preparation.
