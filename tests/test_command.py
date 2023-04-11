import pytest
from src.commands.command import BaseCommand, GoogleCommand, MemoryAddCommand, CommandFactory, execute_command

class TestCommands:
    def test_base_command(self):
        with pytest.raises(TypeError):
            base_command = BaseCommand({})

    def test_google_command(self):
        google_command = GoogleCommand({"query": "OpenAI"})
        # Uncomment the following line when you have implemented the GoogleCommand execute method
        # assert google_command.execute() is not None

    def test_memory_add_command(self):
        memory_add_command = MemoryAddCommand({"memory": "Remember this"})
        # Uncomment the following line when you have implemented the MemoryAddCommand execute method
        # assert memory_add_command.execute() is not None

    def test_command_factory(self):
        google_command = CommandFactory.create_command("google", {"query": "OpenAI"})
        assert isinstance(google_command, GoogleCommand)

        memory_add_command = CommandFactory.create_command("memory_add", {"memory": "Remember this"})
        assert isinstance(memory_add_command, MemoryAddCommand)

        with pytest.raises(ValueError):
            CommandFactory.create_command("unknown", {})

    def test_execute_command(self):
        # Uncomment the following lines when you have implemented the GoogleCommand and MemoryAddCommand execute methods
        # result_google = execute_command("google", {"query": "OpenAI"})
        # assert result_google is not None

        # result_memory_add = execute_command("memory_add", {"memory": "Remember this"})
        # assert result_memory_add is not None

        result_error = execute_command("unknown", {})
        assert "Error:" in result_error