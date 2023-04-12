import typer
from colorama import Fore
from colorama import Style

import commands as cmd
import utils
from configs import Config
from memories import get_memory
from src.configs.agi_config import AGIConfig
from src.display.print import print_assistant_thoughts
from src.display.print import print_to_console
from src.display.spinner import Spinner
from src.llms.OpenAI import ChatAssistant
from src.utils.logs import configure_logging

app = typer.Typer()


class AutoGPT:
    def __init__(self):
        self.cfg = Config()
        self.agi_name = ""
        self.full_message_history = []
        self.next_action_count = 0
        self.memory = None
        self.chat = ChatAssistant()

    def construct_prompt(self) -> str:
        """Construct the prompt for the AI to respond to"""
        config = AGIConfig.load()
        if config.agi_name:
            print_to_console(
                "Welcome back! ",
                Fore.GREEN,
                f"Would you like me to return to being {config.ai_name}?",
                speak_text=True,
            )
            should_continue = utils.clean_input(
                f"""Continue with the last settings?
    Name:  {config.agi_name}
    Role:  {config.agi_role}
    Goals: {config.agi_goals}
    Continue (y/n): """
            )
            if should_continue.lower() == "n":
                config = AGIConfig()

        if not config.agi_name:
            config = self.prompt_user()
            config.save()

        # Get rid of this global:
        global agi_name
        agi_name = config.agi_name

        return config.construct_full_prompt()

    def prompt_user(self) -> AGIConfig:
        """Prompt the user for input"""
        agi_name = ""
        # Construct the prompt
        print_to_console(
            "Welcome to AGI! ",
            Fore.GREEN,
            "Enter the name of your AI and its role below. Entering nothing will load defaults.",
            speak_text=True,
        )

        # Get AI Name from User
        print_to_console(
            "Name your AI: ", Fore.GREEN, "For example, 'Entrepreneur-GPT'"
        )
        agi_name = utils.clean_input("AI Name: ")
        if agi_name == "":
            agi_name = "Entrepreneur-GPT"

        print_to_console(
            f"{agi_name} here!",
            Fore.LIGHTBLUE_EX,
            "I am at your service.",
            speak_text=True,
        )

        # Get AI Role from User
        print_to_console(
            "Describe your AI's role: ",
            Fore.GREEN,
            "For example, 'an AI designed to autonomously develop and run businesses with the sole goal of increasing your net worth.'",
        )
        agi_role = utils.clean_input(f"{agi_name} is: ")
        if agi_role == "":
            agi_role = "an AI designed to autonomously develop and run businesses with the sole goal of increasing your net worth."

        # Enter up to 5 goals for the AI
        print_to_console(
            "Enter up to 5 goals for your AI: ",
            Fore.GREEN,
            "For example: \nIncrease net worth, Grow Twitter Account, Develop and manage multiple businesses autonomously'",
        )
        print(
            "Enter nothing to load defaults, enter nothing when finished.", flush=True
        )
        ai_goals = []
        for i in range(5):
            ai_goal = utils.clean_input(
                f"{Fore.LIGHTBLUE_EX}Goal{Style.RESET_ALL} {i+1}: "
            )
            if ai_goal == "":
                break
            ai_goals.append(ai_goal)
        if not ai_goals:
            ai_goals = [
                "Increase net worth",
                "Grow Twitter Account",
                "Develop and manage multiple businesses autonomously",
            ]

        return AGIConfig(agi_name, agi_role, ai_goals)

    def parse_arguments(
        self, continuous: bool, speak: bool, debug: bool, gpt3only: bool
    ):
        """Parses the arguments passed to the script"""
        self.cfg.continuous_mode = continuous
        self.cfg.speak = speak
        self.cfg.debug = debug
        self.cfg.gpt3only = gpt3only

    def main_loop(self):
        # TODO: fill in llm values here
        self.cfg.check_openai_api_key()
        configure_logging()
        self.parse_arguments()
        ai_name = ""
        prompt = self.construct_prompt()
        # print(prompt)
        # Initialize variables
        full_message_history = []
        result = None
        next_action_count = 0
        # Make a constant:
        user_input = "Determine which next command to use, and respond using the format specified above:"

        # Initialize memory and make sure it is empty.
        # this is particularly important for indexing and referencing pinecone memory
        memory = get_memory(self.cfg, init=True)
        print(f"Using memory of type: {memory.__class__.__name__}")

        # Interaction Loop
        while True:
            # Send message to AI, get response
            with Spinner("Thinking... "):
                assistant_reply = chat.chat_with_ai(
                    prompt,
                    user_input,
                    full_message_history,
                    memory,
                    cfg.fast_token_limit,
                )  # TODO: This hardcodes the model to use GPT3.5. Make this an argument

            # Print Assistant thoughts
            print_assistant_thoughts(assistant_reply)

            # Get command name and arguments
            try:
                command_name, arguments = cmd.get_command(assistant_reply)
            except Exception as e:
                print_to_console("Error: \n", Fore.RED, str(e))

            if not self.cfg.continuous_mode and next_action_count == 0:
                ### GET USER AUTHORIZATION TO EXECUTE COMMAND ###
                # Get key press: Prompt the user to press enter to continue or escape
                # to exit
                user_input = ""
                print_to_console(
                    "NEXT ACTION: ",
                    Fore.CYAN,
                    f"COMMAND = {Fore.CYAN}{command_name}{Style.RESET_ALL}  ARGUMENTS = {Fore.CYAN}{arguments}{Style.RESET_ALL}",
                )
                print(
                    f"Enter 'y' to authorise command, 'y -N' to run N continuous commands, 'n' to exit program, or enter feedback for {ai_name}...",
                    flush=True,
                )
                while True:
                    console_input = utils.clean_input(
                        f"{Fore.MAGENTA}Input:{Style.RESET_ALL}"
                    )
                    if console_input.lower() == "y":
                        user_input = "GENERATE NEXT COMMAND JSON"
                    elif console_input.lower().startswith("y -"):
                        try:
                            next_action_count = abs(int(console_input.split(" ")[1]))
                            user_input = "GENERATE NEXT COMMAND JSON"
                        except ValueError:
                            print(
                                "Invalid input format. Please enter 'y -n' where n is the number of continuous tasks."
                            )
                            continue
                    elif console_input.lower() == "n":
                        user_input = "EXIT"
                    else:
                        user_input = console_input
                        command_name = "human_feedback"
                    break
                if user_input == "GENERATE NEXT COMMAND JSON":
                    print_to_console(
                        "-=-=-=-=-=-=-= COMMAND AUTHORISED BY USER -=-=-=-=-=-=-=",
                        Fore.MAGENTA,
                        "",
                    )
                elif user_input == "EXIT":
                    print("Exiting...", flush=True)
                    break
            else:
                # Print command
                print_to_console(
                    "NEXT ACTION: ",
                    Fore.CYAN,
                    f"COMMAND = {Fore.CYAN}{command_name}{Style.RESET_ALL}  ARGUMENTS = {Fore.CYAN}{arguments}{Style.RESET_ALL}",
                )

            # Execute command
            if command_name.lower().startswith("error"):
                result = (
                    f"Command {command_name} threw the following error: {arguments}"
                )
            elif command_name == "human_feedback":
                result = f"Human feedback: {user_input}"
            else:
                result = f"Command {command_name} returned: {cmd.execute_command(command_name, arguments)}"
                if next_action_count > 0:
                    next_action_count -= 1

            memory_to_add = (
                f"Assistant Reply: {assistant_reply} "
                f"\nResult: {result} "
                f"\nHuman Feedback: {user_input} "
            )

            memory.add(memory_to_add)

            # Check if there's a result from the command append it to the message
            # history
            if result is not None:
                full_message_history.append(
                    self.chat.create_chat_message("system", result)
                )
                print_to_console("SYSTEM: ", Fore.YELLOW, result)
            else:
                full_message_history.append(
                    self.chat.create_chat_message("system", "Unable to execute command")
                )
                print_to_console("SYSTEM: ", Fore.YELLOW, "Unable to execute command")


def main(
    continuous: bool = typer.Option(False, help="Enable Continuous Mode"),
    speak: bool = typer.Option(False, help="Enable Speak Mode"),
    debug: bool = typer.Option(False, help="Enable Debug Mode"),
    gpt3only: bool = typer.Option(False, help="Enable GPT3.5 Only Mode"),
):
    auto_gpt = AutoGPT()
    auto_gpt.parse_arguments(continuous, speak, debug, gpt3only)
    auto_gpt.construct_prompt()

    auto_gpt.memory = get_memory(auto_gpt.cfg, init=True)
    print(f"Using memory of type: {auto_gpt.memory.__class__.__name__}")

    auto_gpt.main_loop()


if __name__ == "__main__":
    main()
