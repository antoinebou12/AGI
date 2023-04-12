import json
import traceback

from rich.console import Console
from rich.text import Text

from functions.speak import speak
from utils.json_parser import fix_and_parse_json

console = Console()


def print_to_console(title, title_color, content, speak_text=False):
    global cfg
    global logger
    if speak_text and cfg.speak_mode:
        speak.say_text(f"{title}. {content}")

    title_text = Text(title, style=title_color)
    content_text = Text(content)
    console.print(title_text, content_text, sep=" ")


def print_assistant_thoughts(assistant_reply):
    global ai_name
    global cfg
    try:
        _extracted_from_print_assistant_thoughts(assistant_reply, ai_name, cfg)
    except json.decoder.JSONDecodeError:
        print_to_console("Error: Invalid JSON\n", "red", assistant_reply)

    except Exception:
        call_stack = traceback.format_exc()
        print_to_console("Error: \n", "red", call_stack)


def _extracted_from_print_assistant_thoughts(assistant_reply, ai_name, cfg):
    assistant_reply_json = fix_and_parse_json(assistant_reply)

    if isinstance(assistant_reply_json, str):
        try:
            assistant_reply_json = json.loads(assistant_reply_json)
        except json.JSONDecodeError as e:
            print_to_console("Error: Invalid JSON\n", "red", assistant_reply)
            assistant_reply_json = {}

    assistant_thoughts = assistant_reply_json.get("thoughts", {})
    assistant_thoughts_text = assistant_thoughts.get("text")
    assistant_thoughts_reasoning = assistant_thoughts.get("reasoning")
    assistant_thoughts_plan = assistant_thoughts.get("plan")
    assistant_thoughts_criticism = assistant_thoughts.get("criticism")
    assistant_thoughts_speak = assistant_thoughts.get("speak")

    print_to_console(f"{ai_name.upper()} THOUGHTS:", "yellow", assistant_thoughts_text)
    print_to_console("REASONING:", "yellow", assistant_thoughts_reasoning)

    if assistant_thoughts_plan:
        print_to_console("PLAN:", "yellow", "")
        if isinstance(assistant_thoughts_plan, list):
            assistant_thoughts_plan = "\n".join(assistant_thoughts_plan)
        elif isinstance(assistant_thoughts_plan, dict):
            assistant_thoughts_plan = str(assistant_thoughts_plan)

        lines = assistant_thoughts_plan.split("\n")
        for line in lines:
            line = line.lstrip("- ")
            print_to_console("- ", "green", line.strip())

    print_to_console("CRITICISM:", "yellow", assistant_thoughts_criticism)

    if cfg.speak_mode and assistant_thoughts_speak:
        speak.say_text(assistant_thoughts_speak)
