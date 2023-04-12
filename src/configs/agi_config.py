import os

import data
import yaml


class AGIConfig:
    """
    A class object that contains the configuration information for the AI

    Attributes:
        agi_name (str): The name of the AI.
        agi_role (str): The description of the AI's role.
        agi_goals (list): The list of objectives the AI is supposed to complete.
    """

    def __init__(
        self, agi_name: str = "", agi_role: str = "", agi_goals: list = None
    ) -> None:
        """
        Initialize a class instance

        Parameters:
            agi_name (str): The name of the AI.
            agi_role (str): The description of the AI's role.
            agi_goals (list): The list of objectives the AI is supposed to complete.
        Returns:
            None
        """

        if agi_goals is None:
            agi_goals = []
        self.agi_name = agi_name
        self.agi_role = agi_role
        self.agi_goals = agi_goals

    # Soon this will go in a folder where it remembers more stuff about the run(s)
    SAVE_FILE = os.path.join(os.path.dirname(__file__), "..", "ai_settings.yaml")

    @classmethod
    def load(cls: object, config_file: str = SAVE_FILE) -> object:
        """
        Returns class object with parameters (agi_name, agi_role, agi_goals) loaded from yaml file if yaml file exists,
        else returns class with no parameters.

        Parameters:
           cls (class object): An AGIConfig Class object.
           config_file (int): The path to the config yaml file. DEFAULT: "../ai_settings.yaml"

        Returns:
            cls (object): A instance of given cls object
        """

        try:
            with open(config_file) as file:
                config_params = yaml.load(file, Loader=yaml.FullLoader)
        except FileNotFoundError:
            config_params = {}

        agi_name = config_params.get("agi_name", "")
        agi_role = config_params.get("agi_role", "")
        agi_goals = config_params.get("agi_goals", [])

        return cls(agi_name, agi_role, agi_goals)

    def save(self, config_file: str = SAVE_FILE) -> None:
        """
        Saves the class parameters to the specified file yaml file path as a yaml file.

        Parameters:
            config_file(str): The path to the config yaml file. DEFAULT: "../ai_settings.yaml"

        Returns:
            None
        """

        config = {
            "agi_name": self.agi_name,
            "agi_role": self.agi_role,
            "agi_goals": self.agi_goals,
        }
        with open(config_file, "w") as file:
            yaml.dump(config, file)

    def construct_full_prompt(self) -> str:
        """
        Returns a prompt to the user with the class information in an organized fashion.

        Parameters:
            None

        Returns:
            full_prompt (str): A string containing the intitial prompt for the user including the agi_name, agi_role and agi_goals.
        """

        prompt_start = """Your decisions must always be made independently without seeking user assistance. Play to your strengths as an LLM and pursue simple strategies with no legal complications."""

        # Construct full prompt
        full_prompt = (
            f"You are {self.agi_name}, {self.agi_role}\n{prompt_start}\n\nGOALS:\n\n"
        )
        for i, goal in enumerate(self.agi_goals):
            full_prompt += f"{i+1}. {goal}\n"

        full_prompt += f"\n\n{data.load_prompt()}"
        return full_prompt
