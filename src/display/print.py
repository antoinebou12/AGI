import json
import traceback

from rich.console import Console
from rich.text import Text

from functions.speak import speak
from src.utils.json import fix_and_parse_json


class AssistantPrinter:
    def __init__(self, cfg, logger, ai_name="Assistant"):
        self.cfg = cfg
        self.logger = logger
        self.ai_name = ai_name
        self.console = Console()

    def print_to_console(self, title, title_color, content, speak_text=False):
        if speak_text and self.cfg.speak_mode:
            speak.say_text(f"{title}. {content}")

        title_text = Text(title, style=title_color)
        content_text = Text(content)
        self.console.print(title_text, content_text, sep=" ")

    def print_assistant_thoughts(self, assistant_reply):
        try:
            self._extracted_from_print_assistant_thoughts(assistant_reply)
        except json.decoder.JSONDecodeError:
            self.print_to_console("Error: Invalid JSON\n", "red", assistant_reply)

        except Exception:
            call_stack = traceback.format_exc()
            self.print_to_console("Error: \n", "red", call_stack)

    def _extracted_from_print_assistant_thoughts(self, assistant_reply):
        assistant_reply_json = fix_and_parse_json(assistant_reply)

        if isinstance(assistant_reply_json, str):
            try:
                assistant_reply_json = json.loads(assistant_reply_json)
            except json.JSONDecodeError as e:
                self.print_to_console("Error: Invalid JSON\n", "red", assistant_reply)
                assistant_reply_json = {}

        assistant_thoughts = assistant_reply_json.get("thoughts", {})
        assistant_thoughts_text = assistant_thoughts.get("text")
        assistant_thoughts_reasoning = assistant_thoughts.get("reasoning")
        assistant_thoughts_plan = assistant_thoughts.get("plan")
        assistant_thoughts_criticism = assistant_thoughts.get("criticism")
        assistant_thoughts_speak = assistant_thoughts.get("speak")

        self.print_to_console(
            f"{self.ai_name.upper()} THOUGHTS:", "yellow", assistant_thoughts_text
        )
        self.print_to_console("REASONING:", "yellow", assistant_thoughts_reasoning)

        if assistant_thoughts_plan:
            self.print_to_console("PLAN:", "yellow", "")
            if isinstance(assistant_thoughts_plan, list):
                assistant_thoughts_plan = "\n".join(assistant_thoughts_plan)
            elif isinstance(assistant_thoughts_plan, dict):
                assistant_thoughts_plan = str(assistant_thoughts_plan)

            lines = assistant_thoughts_plan.split("\n")
            for line in lines:
                line = line.lstrip("- ")
                self.print_to_console("- ", "green", line.strip())

        self.print_to_console("CRITICISM:", "yellow", assistant_thoughts_criticism)

        if self.cfg.speak_mode and assistant_thoughts_speak:
            speak.say_text(assistant_thoughts_speak)
