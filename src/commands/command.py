import json
from abc import ABC
from abc import abstractmethod

from commands.google import GoogleCommand
from commands.memory import MemoryAddCommand
from configs import Config

cfg = Config()


class BaseCommand(ABC):
    def __init__(self, arguments):
        self.arguments = arguments

    @abstractmethod
    def execute(self):
        pass


class CommandFactory:
    @staticmethod
    def create_command(command_name, arguments):
        if command_name == "google":
            return GoogleCommand(arguments)
        elif command_name == "memory_add":
            return MemoryAddCommand(arguments)
        else:
            raise ValueError(f"Unknown command '{command_name}'")


def execute_command(command_name, arguments):
    try:
        command = CommandFactory.create_command(command_name, arguments)
        return command.execute()
    except Exception as e:
        return f"Error: {str(e)}"


def get_command(response):
    try:
        response_json = json.loads(response)

        if "command" not in response_json:
            return "Error:", "Missing 'command' object in JSON"

        command = response_json["command"]

        if "name" not in command:
            return "Error:", "Missing 'name' field in 'command' object"

        command_name = command["name"]
        arguments = command.get("args", {})

        return command_name, arguments
    except json.JSONDecodeError:
        return "Error:", "Invalid JSON"
    except Exception as e:
        return "Error:", str(e)
