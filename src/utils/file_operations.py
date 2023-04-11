import os
import os.path
from rich.console import Console

console = Console()

# Set a dedicated folder for file I/O
working_directory = "agi_workspace"

# Create the directory if it doesn't exist
if not os.path.exists(working_directory):
    os.makedirs(working_directory)


def safe_join(base, *paths):
    """Join one or more path components intelligently."""
    new_path = os.path.join(base, *paths)
    norm_new_path = os.path.normpath(new_path)

    if os.path.commonprefix([base, norm_new_path]) != base:
        raise ValueError("Attempted to access outside of working directory.")

    return norm_new_path

def read_file(filename):
    """Read a file and return the contents"""
    try:
        filepath = safe_join(working_directory, filename)
        with open(filepath, "r", encoding='utf-8') as f:
            content = f.read()
        console.print(f"[green]File read successfully: {filename}")
        return content
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        return ""


def write_to_file(filename, text):
    """Write text to a file"""
    try:
        filepath = safe_join(working_directory, filename)
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(filepath, "w") as f:
            f.write(text)
        console.print(f"[green]File written to successfully: {filename}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


def append_to_file(filename, text):
    """Append text to a file"""
    try:
        filepath = safe_join(working_directory, filename)
        with open(filepath, "a") as f:
            f.write(text)
        console.print(f"[green]Text appended successfully: {filename}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


def delete_file(filename):
    """Delete a file"""
    try:
        filepath = safe_join(working_directory, filename)
        os.remove(filepath)
        console.print(f"[green]File deleted successfully: {filename}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


def search_files(directory):
    found_files = []

    if directory == "" or directory == "/":
        search_directory = working_directory
    else:
        search_directory = safe_join(working_directory, directory)

    for root, _, files in os.walk(search_directory):
        for file in files:
            if file.startswith('.'):
                continue
            relative_path = os.path.relpath(os.path.join(root, file), working_directory)
            found_files.append(relative_path)

    console.print("[cyan]Found files:")
    for file in found_files:
        console.print(f"[green]->[/green] {file}")

    return found_files
