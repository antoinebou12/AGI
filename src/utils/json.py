# -*- coding: utf-8 -*-
import contextlib
import json
import re
from typing import Any
from typing import Dict
from typing import Union

from rich import Console

from configs import Config
from llms.CodeAssistant import call_ai_function

cfg = Config()


class JSON:
    JSON_SCHEMA = """
    {
        "command": {
            "name": "command name",
            "args":{
                "arg name": "value"
            }
        },
        "thoughts":
        {
            "text": "thought",
            "reasoning": "reasoning",
            "plan": "- short bulleted\n- list that conveys\n- long-term plan",
            "criticism": "constructive self-criticism",
            "speak": "thoughts summary to say to user"
        }
    }
    """

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.console = Console()

    def fix_and_parse_json(
        self, json_str: str, try_to_fix_with_gpt: bool = True
    ) -> Union[str, Dict[Any, Any]]:
        """Fix and parse JSON string"""
        try:
            json_str = json_str.replace("\t", "")
            return json.loads(json_str)
        except json.JSONDecodeError as _:  # noqa: F841
            json_str = correct_json(json_str)
            with contextlib.suppress(json.JSONDecodeError):
                return json.loads(json_str)
        # Let's do something manually:
        # sometimes GPT responds with something BEFORE the braces:
        # "I'm sorry, I don't understand. Please try again."
        # {"text": "I'm sorry, I don't understand. Please try again.",
        #  "confidence": 0.0}
        # So let's try to find the first brace and then parse the rest
        #  of the string
        try:
            brace_index = json_str.index("{")
            json_str = json_str[brace_index:]
            last_brace_index = json_str.rindex("}")
            json_str = json_str[: last_brace_index + 1]
            return json.loads(json_str)
        except json.JSONDecodeError as e:  # noqa: F841
            return self.failed_parse(try_to_fix_with_gpt, e, json_str)

    def failed_parse(self, try_to_fix_with_gpt, e, json_str):
        if not try_to_fix_with_gpt:
            raise e
        self.console.print(
            "Warning: Failed to parse AI output, attempting to fix."
            "\n If you see this warning frequently, it's likely that"
            " your prompt is confusing the AI. Try changing it up"
            " slightly."
        )
        # Now try to fix this up using the ai_functions
        ai_fixed_json = call_ai_function("fix_json", json_str, self.JSON_SCHEMA)

        if ai_fixed_json != "failed":
            return json.loads(ai_fixed_json)
        # This allows the AI to react to the error
        raise e

    def correct_json(self, json_str: str) -> str:
        """Fix the given JSON string to make it parseable and fully complient with the provided schema."""
        # Try to fix the JSON using gpt:
        function_string = "def fix_json(json_str: str, schema:str=None) -> str:"
        args = [f"'''{json_str}'''", f"'''{self.JSON_SCHEMA}'''"]
        description_string = (
            "Fixes the provided JSON string to make it parseable"
            " and fully complient with the provided schema.\n If an object or"
            " field specified in the schema isn't contained within the correct"
            " JSON, it is ommited.\n This function is brilliant at guessing"
            " when the format is incorrect."
        )

        # If it doesn't already start with a "`", add one:
        if not json_str.startswith("`"):
            json_str = "```json\n" + json_str + "\n```"
        result_string = call_ai_function(
            function_string, args, description_string, model=self.cfg.fast_llm_model
        )
        if self.cfg.debug:
            self.console.print("------------ JSON FIX ATTEMPT ---------------")
            self.console.print(f"Original JSON: {json_str}")
            self.console.print("-----------")
            self.console.print(f"Fixed JSON: {result_string}")
            self.console.print("----------- END OF FIX ATTEMPT ----------------")

        try:
            json.loads(result_string)  # just check the validity
            return result_string
        except Exception:
            # Get the call stack:
            # import traceback
            # call_stack = traceback.format_exc()
            # print(f"Failed to fix JSON: '{json_str}' "+call_stack)
            return "failed"

    def extract_char_position(self, error_message: str) -> int:
        """Extract the character position from the JSONDecodeError message.

        Args:
            error_message (str): The error message from the JSONDecodeError
            exception.

        Returns:
            int: The character position.
        """

        char_pattern = re.compile(r"\(char (\d+)\)")
        if match := char_pattern.search(error_message):
            return int(match[1])
        else:
            raise ValueError("Character position not found in the error message.")

    def add_quotes_to_property_names(self, json_string: str) -> str:
        """
        Add quotes to property names in a JSON string.

        Args:
            json_string (str): The JSON string.

        Returns:
            str: The JSON string with quotes added to property names.
        """

        def replace_func(match):
            return f'"{match.group(1)}":'

        property_name_pattern = re.compile(r"(\w+):")
        corrected_json_string = property_name_pattern.sub(replace_func, json_string)

        try:
            json.loads(corrected_json_string)
            return corrected_json_string
        except json.JSONDecodeError as e:
            raise e

    def balance_braces(self, json_string: str) -> str:
        """
        Balance the braces in a JSON string.

        Args:
            json_string (str): The JSON string.

        Returns:
            str: The JSON string with braces balanced.
        """

        open_braces_count = json_string.count("{")
        close_braces_count = json_string.count("}")

        while open_braces_count > close_braces_count:
            json_string += "}"
            close_braces_count += 1

        while close_braces_count > open_braces_count:
            json_string = json_string.rstrip("}")
            close_braces_count -= 1

        with contextlib.suppress(json.JSONDecodeError):
            json.loads(json_string)
            return json_string

    def fix_invalid_escape(self, json_str: str, error_message: str) -> str:
        while error_message.startswith("Invalid \\escape"):
            bad_escape_location = extract_char_position(error_message)
            json_str = (
                json_str[:bad_escape_location] + json_str[bad_escape_location + 1 :]
            )
            try:
                json.loads(json_str)
                return json_str
            except json.JSONDecodeError as e:
                if cfg.debug_mode:
                    print("json loads error - fix invalid escape", e)
                error_message = str(e)
        return json_str

    def correct_json(self, json_str: str) -> str:
        """
        Correct common JSON errors.

        Args:
            json_str (str): The JSON string.
        """

        try:
            if cfg.debug_mode:
                print("json", json_str)
            json.loads(json_str)
            return json_str
        except json.JSONDecodeError as e:
            if cfg.debug_mode:
                print("json loads error", e)
            error_message = str(e)
            if error_message.startswith("Invalid \\escape"):
                json_str = self.fix_invalid_escape(json_str, error_message)
            if error_message.startswith(
                "Expecting property name enclosed in double quotes"
            ):
                json_str = self.add_quotes_to_property_names(json_str)
                try:
                    json.loads(json_str)
                    return json_str
                except json.JSONDecodeError as e:
                    if cfg.debug_mode:
                        print("json loads error - add quotes", e)
                    error_message = str(e)
            if balanced_str := self.balance_braces(json_str):
                return balanced_str
        return json_str
