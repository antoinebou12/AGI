# -*- coding: utf-8 -*-
import abc
import os

import openai
import yaml
from dotenv import load_dotenv

from src.prompts.prompt import load_prompt
from utils.utils import clean_input

# Load environment variables from .env file
load_dotenv()


class Singleton(abc.ABCMeta, type):
    """
    Singleton metaclass for ensuring only one instance of a class.
    """

    _instances = {}

    def __call__(self, *args, **kwargs):
        """Call method for the singleton metaclass."""
        if self not in self._instances:
            self._instances[self] = super().__call__(*args, **kwargs)
        return self._instances[self]


class AbstractSingleton(abc.ABC, metaclass=Singleton):
    pass


class AGIConfig(AbstractSingleton):
    """
    Configuration class to store the state of bools for different scripts access.
    """

    def __init__(self):
        """Initialize the Config class"""
        self.load_environment_variables()
        self.load_ai_settings(config_file)
        self.debug_mode = False
        self.continuous_mode = False
        self.speak_mode = False

        self.fast_llm_model = os.getenv("FAST_LLM_MODEL", "gpt-3.5-turbo")
        self.smart_llm_model = os.getenv("SMART_LLM_MODEL", "gpt-4")
        self.fast_token_limit = int(os.getenv("FAST_TOKEN_LIMIT", 4000))
        self.smart_token_limit = int(os.getenv("SMART_TOKEN_LIMIT", 8000))

        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.use_azure = False
        self.use_azure = os.getenv("USE_AZURE") == "True"
        if self.use_azure:
            self.openai_api_base = os.getenv("OPENAI_AZURE_API_BASE")
            self.openai_api_version = os.getenv("OPENAI_AZURE_API_VERSION")
            self.openai_deployment_id = os.getenv("OPENAI_AZURE_DEPLOYMENT_ID")
            openai.api_type = "azure"
            openai.api_base = self.openai_api_base
            openai.api_version = self.openai_api_version

        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")

        self.use_mac_os_tts = False
        self.use_mac_os_tts = os.getenv("USE_MAC_OS_TTS")

        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.custom_search_engine_id = os.getenv("CUSTOM_SEARCH_ENGINE_ID")

        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_region = os.getenv("PINECONE_ENV")

        self.image_provider = os.getenv("IMAGE_PROVIDER")
        self.huggingface_api_token = os.getenv("HUGGINGFACE_API_TOKEN")

        # User agent headers to use when browsing web
        # Some websites might just completely deny request with an error code if no user agent was found.
        self.user_agent_header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
        }
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = os.getenv("REDIS_PORT", "6379")
        self.redis_password = os.getenv("REDIS_PASSWORD", "")
        self.wipe_redis_on_start = os.getenv("WIPE_REDIS_ON_START", "True") == "True"
        self.memory_index = os.getenv("MEMORY_INDEX", "auto-gpt")
        # Note that indexes must be created on db 0 in redis, this is not configureable.

        self.memory_backend = os.getenv("MEMORY_BACKEND", "local")
        # Initialize the OpenAI API client
        openai.api_key = self.openai_api_key

    def set_continuous_mode(self, value: bool):
        """Set the continuous mode value."""
        self.continuous_mode = value

    def set_speak_mode(self, value: bool):
        """Set the speak mode value."""
        self.speak_mode = value

    def set_fast_llm_model(self, value: str):
        """Set the fast LLM model value."""
        self.fast_llm_model = value

    def set_smart_llm_model(self, value: str):
        """Set the smart LLM model value."""
        self.smart_llm_model = value

    def set_fast_token_limit(self, value: int):
        """Set the fast token limit value."""
        self.fast_token_limit = value

    def set_smart_token_limit(self, value: int):
        """Set the smart token limit value."""
        self.smart_token_limit = value

    def set_openai_api_key(self, value: str):
        """Set the OpenAI API key value."""
        self.openai_api_key = value

    def set_elevenlabs_api_key(self, value: str):
        """Set the ElevenLabs API key value."""
        self.elevenlabs_api_key = value

    def set_google_api_key(self, value: str):
        """Set the Google API key value."""
        self.google_api_key = value

    def set_custom_search_engine_id(self, value: str):
        """Set the custom search engine id value."""
        self.custom_search_engine_id = value

    def set_pinecone_api_key(self, value: str):
        """Set the Pinecone API key value."""
        self.pinecone_api_key = value

    def set_pinecone_region(self, value: str):
        """Set the Pinecone region value."""
        self.pinecone_region = value

    def set_debug_mode(self, value: bool):
        """Set the debug mode value."""
        self.debug_mode = value

    def check_openai_api_key(self):
        """Check if the OpenAI API key is set in config.py or as an environment variable."""
        if not cfg.openai_api_key:
            print(
                Fore.RED
                + "Please set your OpenAI API key in config.py or as an environment variable."
            )
            print("You can get your key from https://beta.openai.com/account/api-keys")
            exit(1)

    def load_variables(self, config_file="config.yaml"):
        """Load variables from yaml file if it exists, otherwise prompt the user for input"""
        try:
            with open(config_file) as file:
                config = yaml.load(file, Loader=yaml.FullLoader)
            agi_name = config.get("agi_name")
            agi_role = config.get("agi_role")
            agi_goals = config.get("agi_goals")
        except FileNotFoundError:
            agi_name = ""
            agi_role = ""
            agi_goals = []

        # Prompt the user for input if config file is missing or empty values
        if not agi_name:
            agi_name = clean_input("Name your AI: ")
            if agi_name == "":
                agi_name = "Entrepreneur-GPT"

        if not agi_role:
            agi_role = clean_input(f"{agi_name} is: ")
            if agi_role == "":
                agi_role = "an AI designed to autonomously develop and run businesses with the sole goal of increasing your net worth."

        if not ai_goals:
            ai_goals = self._extracted_from_load_variables_26(agi_goals)
        # Save variables to yaml file
        config = {"agi_name": agi_name, "agi_role": agi_role, "agi_goals": ai_goals}
        with open(config_file, "w") as file:
            yaml.dump(config, file)

        prompt = load_prompt()
        prompt_start = """Your decisions must always be made independently without seeking user assistance. Play to your strengths as a LLM and pursue simple strategies with no legal complications."""

        # Construct full prompt
        full_prompt = f"You are {agi_name}, {agi_role}\n{prompt_start}\n\nGOALS:\n\n"
        for i, goal in enumerate(ai_goals):
            full_prompt += f"{i+1}. {goal}\n"

        full_prompt += f"\n\n{prompt}"
        return full_prompt

    def _extracted_from_load_variables_26(self, agi_goals):
        print("Enter up to 5 goals for your AI: ")
        print(
            "For example: \nIncrease net worth, Grow Twitter Account, Develop and manage multiple businesses autonomously'"
        )
        print("Enter nothing to load defaults, enter nothing when finished.")
        for i in range(5):
            agi_goal = clean_input(f"Goal {i+1}: ")
            if agi_goal == "":
                break
            agi_goals.append(agi_goal)
        if not agi_goals:
            agi_goals = [
                "Increase net worth",
                "Grow Twitter Account",
                "Develop and manage multiple businesses autonomously",
            ]

        return []


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

        full_prompt += f"\n\n{load_prompt()}"
        return full_prompt
