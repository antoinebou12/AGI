from pathlib import Path


def load_prompt():
    """Load the prompt from prompt.txt"""
    try:
        return Path("prompt.txt").read_text()
    except FileNotFoundError:
        print("Error: Prompt file not found", flush=True)
        return ""
