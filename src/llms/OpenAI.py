import time
from typing import Dict
from typing import List

import openai
import token_counter
from tiktoken import encoding_for_model
from tiktoken import get_encoding

from configs import Config

cfg = Config()


class ChatAssistant:
    def __init__(self):
        self.cfg = Config()
        self.prompt = ""
        self.model = ""
        self.full_message_history = []
        self.relevant_memory = []
        self.chat = ChatAssistant()
        openai.api_key = self.cfg.openai_api_key

    def create_chat_message(self, role, content):
        """
        Create a chat message with the given role and content.

        Args:
        role (str): The role of the message sender, e.g., "system", "user", or "assistant".
        content (str): The content of the message.

        Returns:
        dict: A dictionary containing the role and content of the message.
        """
        return {"role": role, "content": content}

    def generate_context(self, prompt, relevant_memory, full_message_history, model):
        current_context = [
            self.create_chat_message("system", prompt),
            self.create_chat_message(
                "system", f"The current time and date is {time.strftime('%c')}"
            ),
            self.create_chat_message(
                "system",
                f"This reminds you of these events from your past:\n{relevant_memory}\n\n",
            ),
        ]

        # Add messages from the full message history until we reach the token limit
        next_message_to_add_index = len(full_message_history) - 1
        insertion_index = len(current_context)
        # Count the currently used tokens
        current_tokens_used = token_counter.count_message_tokens(current_context, model)
        return (
            next_message_to_add_index,
            current_tokens_used,
            insertion_index,
            current_context,
        )

    def chat_with_ai(
        self, prompt, user_input, full_message_history, permanent_memory, token_limit
    ):
        """Interact with the OpenAI API, sending the prompt, user input, message history, and permanent memory."""
        while True:
            try:
                """
                Interact with the OpenAI API, sending the prompt, user input, message history, and permanent memory.

                Args:
                prompt (str): The prompt explaining the rules to the AI.
                user_input (str): The input from the user.
                full_message_history (list): The list of all messages sent between the user and the AI.
                permanent_memory (Obj): The memory object containing the permanent memory.
                token_limit (int): The maximum number of tokens allowed in the API call.

                Returns:
                str: The AI's response.
                """
                model = (
                    cfg.fast_llm_model
                )  # TODO: Change model from hardcode to argument
                # Reserve 1000 tokens for the response

                if cfg.debug:
                    print(f"Token limit: {token_limit}")

                send_token_limit = token_limit - 1000

                relevant_memory = permanent_memory.get_relevant(
                    str(full_message_history[-5:]), 10
                )

                if cfg.debug:
                    print("Memory Stats: ", permanent_memory.get_stats())

                (
                    next_message_to_add_index,
                    current_tokens_used,
                    insertion_index,
                    current_context,
                ) = self.generate_context(
                    prompt, relevant_memory, full_message_history, model
                )

                while current_tokens_used > 2500:
                    # remove memories until we are under 2500 tokens
                    relevant_memory = relevant_memory[1:]
                    (
                        next_message_to_add_index,
                        current_tokens_used,
                        insertion_index,
                        current_context,
                    ) = self.generate_context(
                        prompt, relevant_memory, full_message_history, model
                    )

                current_tokens_used += token_counter.count_message_tokens(
                    [self.create_chat_message("user", user_input)], model
                )  # Account for user input (appended later)

                while next_message_to_add_index >= 0:
                    # print (f"CURRENT TOKENS USED: {current_tokens_used}")
                    message_to_add = full_message_history[next_message_to_add_index]

                    tokens_to_add = token_counter.count_message_tokens(
                        [message_to_add], model
                    )
                    if current_tokens_used + tokens_to_add > send_token_limit:
                        break

                    # Add the most recent message to the start of the current context, after the two system prompts.
                    current_context.insert(
                        insertion_index, full_message_history[next_message_to_add_index]
                    )

                    # Count the currently used tokens
                    current_tokens_used += tokens_to_add

                    # Move to the next most recent message in the full message history
                    next_message_to_add_index -= 1

                # Append user input, the length of this is accounted for above
                current_context.extend([self.create_chat_message("user", user_input)])

                # Calculate remaining tokens
                tokens_remaining = token_limit - current_tokens_used
                # assert tokens_remaining >= 0, "Tokens remaining is negative. This should never happen, please submit a bug report at https://www.github.com/Torantulino/Auto-GPT"

                # Debug print the current context
                if cfg.debug:
                    print(f"Token limit: {token_limit}")
                    print(f"Send Token Count: {current_tokens_used}")
                    print(f"Tokens remaining for response: {tokens_remaining}")
                    print("------------ CONTEXT SENT TO AI ---------------")
                    for message in current_context:
                        # Skip printing the prompt
                        if message["role"] == "system" and message["content"] == prompt:
                            continue
                        print(f"{message['role'].capitalize()}: {message['content']}")
                        print()
                    print("----------- END OF CONTEXT ----------------")

                # TODO: use a model defined elsewhere, so that model can contain temperature and other settings we care about
                assistant_reply = self.chat.create_chat_completion(
                    model=model,
                    messages=current_context,
                    max_tokens=tokens_remaining,
                )

                # Update full message history
                full_message_history.append(
                    self.create_chat_message("user", user_input)
                )
                full_message_history.append(
                    self.create_chat_message("assistant", assistant_reply)
                )

                return assistant_reply
            except openai.error.RateLimitError:
                # TODO: WHen we switch to langchain, this is built in
                print("Error: ", "API Rate Limit Reached. Waiting 10 seconds...")
                time.sleep(10)

    def create_chat_completion(
        self, messages, model=None, temperature=None, max_tokens=None
    ) -> str:
        """Create a chat completion using the OpenAI API"""
        if cfg.use_azure:
            response = openai.ChatCompletion.create(
                deployment_id=cfg.openai_deployment_id,
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        else:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        return response.choices[0].message["content"]

    def count_message_tokens(
        self, messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo-0301"
    ) -> int:
        try:
            encoding = encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = get_encoding("cl100k_base")

        tokens_per_message = {"gpt-3.5-turbo-0301": 4, "gpt-4-0314": 3}.get(model)
        tokens_per_name = {"gpt-3.5-turbo-0301": -1, "gpt-4-0314": 1}.get(model)

        if tokens_per_message is None or tokens_per_name is None:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )

        return (
            sum(
                tokens_per_message
                + sum(encoding.encode(value))
                + (tokens_per_name if key == "name" else 0)
                for message in messages
                for key, value in message.items()
            )
            + 3
        )

    def count_string_tokens(self, string: str, model_name: str) -> int:
        """
        Count the number of tokens in a string for a given model.

        :param string: The string to count tokens for.
        :param model_name: The name of the model to use.
        :return: The number of tokens in the string.
        """
        encoding = encoding_for_model(model_name)
        return len(encoding.encode(string))

    def print_model_price(self, model: str):
        model_prices = {
            "gpt4_8k": (0.03, 0.06),
            "gpt4_32k": (0.06, 0.12),
            "chat_gpt": 0.002,
            "ada": (0.0004, 0.0016),
            "babbage": (0.0006, 0.0024),
            "curie": (0.0030, 0.0120),
            "davinci": (0.0300, 0.1200),
            "embedding_ada": 0.0004,
            "embedding_curie": 0.0006,
            "image_1024": 0.020,
            "image_512": 0.018,
            "image_256": 0.016,
            "whisper": 0.006,
        }
        price = model_prices.get(model)
        if price is None:
            print("Invalid model. Please choose a valid model.")

        elif isinstance(price, tuple):
            print(
                f"Model: {model}, Price per token (prompt): ${price[0]:.4f}, Price per token (completion): ${price[1]:.4f}"
            )
        else:
            print(f"Model: {model}, Price per token: ${price:.4f}")
