"""
This is the main entry point of the PDF-GPT4-JSON application.
It runs the CLI (Command Line Interface) defined in the `cli` module.
"""

import typer
from .cli import main

def run():
    typer.run(main)


if __name__ == "__main__":
    run()
