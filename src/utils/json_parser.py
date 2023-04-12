import contextlib
import json
from typing import Any
from typing import Dict
from typing import Union

from json_utils import correct_json

from configs import Config
from llms.CodeAssistant import call_ai_function

cfg = Config()


class JSONFixer:
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
        print(
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
            print("------------ JSON FIX ATTEMPT ---------------")
            print(f"Original JSON: {json_str}")
            print("-----------")
            print(f"Fixed JSON: {result_string}")
            print("----------- END OF FIX ATTEMPT ----------------")

        try:
            json.loads(result_string)  # just check the validity
            return result_string
        except Exception:
            # Get the call stack:
            # import traceback
            # call_stack = traceback.format_exc()
            # print(f"Failed to fix JSON: '{json_str}' "+call_stack)
            return "failed"
