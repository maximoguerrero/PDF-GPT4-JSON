import os
from gpt import process


def main(pdf: str, promptFile: str = None, openaiKey: str = None, verbose: bool = False, cleanup: bool = False):

    if not os.path.exists(pdf):
        print(f"File {pdf} not found")
        return

    api_key = os.getenv("OPENAI_API_KEY")
    if openaiKey:
        api_key = openaiKey

    folder = os.path.dirname(pdf)
    filename = os.path.basename(pdf)

    if verbose:
        print(f"PDF to extract {pdf}")
        print(f"Folder {folder}")
        print(f"Filename {filename}")

    userprompt = None
    if promptFile and os.path.exists(promptFile):
        with open(promptFile, "r") as file:
            userprompt = file.read()

    process(filename, folder, userprompt=userprompt,
            api_key=api_key, verbose=verbose, cleanup=cleanup)
