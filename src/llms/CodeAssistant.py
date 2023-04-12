import json
from typing import List

from configs import Config
from src.llms.llm_utils import create_chat_completion

cfg = Config()


class CodeAssistant:
    def __init__(self):
        self.cfg = Config()
        self.code = ""

    def evaluate_code(self) -> List[str]:
        """
        A function that takes in a string and returns a response from create chat completion api call.

        Parameters:
            code (str): Code to be evaluated.
        Returns:
            A result string from create chat completion. A list of suggestions to improve the code.
        """

        function_string = "def analyze_code(code: str) -> List[str]:"
        args = [self.code]
        description_string = """Analyzes the given code and returns a list of suggestions for improvements."""

        return call_ai_function(function_string, args, description_string)

    def improve_code(self, suggestions: List[str]) -> str:
        """
        A function that takes in code and suggestions and returns a response from create chat completion api call.

        Parameters:
            suggestions (List): A list of suggestions around what needs to be improved.
            code (str): Code to be improved.
        Returns:
            A result string from create chat completion. Improved code in response.
        """

        function_string = (
            "def generate_improved_code(suggestions: List[str], code: str) -> str:"
        )
        args = [json.dumps(suggestions), self.code]
        description_string = """Improves the provided code based on the suggestions provided, making no other changes."""

        return self.call_ai_function(function_string, args, description_string)

    def write_tests(self, focus: List[str]) -> str:
        """
        A function that takes in code and focus topics and returns a response from create chat completion api call.

        Parameters:
            focus (List): A list of suggestions around what needs to be improved.
            code (str): Code for test cases to be generated against.
        Returns:
            A result string from create chat completion. Test cases for the submitted code in response.
        """

        function_string = (
            "def create_test_cases(code: str, focus: Optional[str] = None) -> str:"
        )
        args = [self.code, json.dumps(focus)]
        description_string = """Generates test cases for the existing code, focusing on specific areas if required."""

        return self.call_ai_function(function_string, args, description_string)

    # This is a magic function that can do anything with no-code. See
    # https://github.com/Torantulino/AI-Functions for more info.
    def call_ai_function(self, function, args, description, model=None):
        """Call an AI function"""
        if model is None:
            model = cfg.smart_llm_model
        # For each arg, if any are None, convert to "None":
        args = [str(arg) if arg is not None else "None" for arg in args]
        # parse args to comma seperated string
        args = ", ".join(args)
        messages = [
            {
                "role": "system",
                "content": f"You are now the following python function: ```# {description}\n{function}```\n\nOnly respond with your `return` value.",
            },
            {"role": "user", "content": args},
        ]

        return create_chat_completion(model=model, messages=messages, temperature=0)
