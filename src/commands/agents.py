import agents
from commands.command import BaseCommand
from functions import is_valid_int


class AgentCommand(BaseCommand):
    def __init__(self, name, task, prompt, model=cfg.fast_llm_model):
        super().__init__(name)
        self.task = task
        self.prompt = prompt
        self.model = model

    def execute(self):
        return super().execute()

    def start_agent(self, task, prompt, model=cfg.fast_llm_model):
        """Start an agent with a given name, task, and prompt"""
        global cfg

        # Remove underscores from name
        voice_name = self.replace("_", " ")

        first_message = f"""You are {self}.  Respond with: "Acknowledged"."""
        agent_intro = f"{voice_name} here, Reporting for duty!"

        # Create agent
        if cfg.speak_mode:
            speak.say_text(agent_intro, 1)
        key, ack = agents.create_agent(task, first_message, model)

        if cfg.speak_mode:
            speak.say_text(f"Hello {voice_name}. Your task is as follows. {task}.")

        # Assign task (prompt), get response
        agent_response = message_agent(key, prompt)

        return f"Agent {self} created with key {key}. First response: {agent_response}"

    def message_agent(key, message):
        """Message an agent with a given key and message"""
        global cfg

        # Check if the key is a valid integer
        if is_valid_int(key):
            agent_response = agents.message_agent(int(key), message)
        # Check if the key is a valid string
        elif isinstance(key, str):
            agent_response = agents.message_agent(key, message)
        else:
            return "Invalid key, must be an integer or a string."

        # Speak response
        if cfg.speak_mode:
            speak.say_text(agent_response, 1)
        return agent_response

    def list_agents():
        """List all agents"""
        return agents.list_agents()

    def delete_agent(key):
        """Delete an agent with a given key"""
        result = agents.delete_agent(key)
        return f"Agent {key} deleted." if result else f"Agent {key} does not exist."
