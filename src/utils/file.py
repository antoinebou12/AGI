# -*- coding: utf-8 -*-
import os.path

from rich.console import Console

from src.utils.json import JSON


class FileOperations:
    def __init__(self, working_directory="agi_workspace"):
        self.working_directory = working_directory
        self.console = Console()
        self.json_file = "agi.json"
        self.json = JSON()

        # Create the directory if it doesn't exist
        if not os.path.exists(self.working_directory):
            os.makedirs(self.working_directory)

    def safe_join(self, base, *paths):
        """Join one or more path components intelligently."""
        new_path = os.path.join(base, *paths)
        norm_new_path = os.path.normpath(new_path)

        if os.path.commonprefix([base, norm_new_path]) != base:
            raise ValueError("Attempted to access outside of working directory.")

        return norm_new_path

    def read_file(self, filename):
        """Read a file and return the contents"""
        try:
            filepath = self.safe_join(self.working_directory, filename)
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
            self.console.print(f"Read file: {filename}")
            return content
        except FileNotFoundError:
            self.console.print(f"File not found: {filename}")
            return None

    def append_to_file(self, filename, text):
        """Append text to a file"""
        try:
            filepath = self.json.safe_join(self.working_directory, filename)
            with open(filepath, "a") as f:
                f.write(text)
            self.console.print(f"[green]Text appended successfully: {filename}")
        except Exception as e:
            self.console.print(f"[red]Error:[/red] {str(e)}")

    def delete_file(self, filename):
        """Delete a file"""
        try:
            filepath = self.json.safe_join(self.working_directory, filename)
            os.remove(filepath)
            self.console.print(f"[green]File deleted successfully: {filename}")
        except Exception as e:
            self.consoleconsole.print(f"[red]Error:[/red] {str(e)}")

    def search_files(self, directory):
        found_files = []

        if directory in ["", "/"]:
            search_directory = self.working_directory
        else:
            search_directory = self.json.safe_join(self.working_directory, directory)

        for root, _, files in os.walk(search_directory):
            for file in files:
                if file.startswith("."):
                    continue
                relative_path = os.path.relpath(
                    os.path.join(root, file), self.working_directory
                )
                found_files.append(relative_path)

        self.console.print("[cyan]Found files:")
        for file in found_files:
            self.console.print(f"[green]->[/green] {file}")

        return found_files
