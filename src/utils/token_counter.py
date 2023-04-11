import tiktoken
from typing import List, Dict

def count_message_tokens(messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo-0301") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")

    tokens_per_message = {"gpt-3.5-turbo-0301": 4, "gpt-4-0314": 3}.get(model)
    tokens_per_name = {"gpt-3.5-turbo-0301": -1, "gpt-4-0314": 1}.get(model)

    if tokens_per_message is None or tokens_per_name is None:
        raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")

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

def count_string_tokens(string: str, model_name: str) -> int:
    """
    Count the number of tokens in a string for a given model.

    :param string: The string to count tokens for.
    :param model_name: The name of the model to use.
    :return: The number of tokens in the string.
    """
    encoding = tiktoken.encoding_for_model(model_name)
    return len(encoding.encode(string))

def print_model_price(model: str):
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
        "whisper": 0.006
    }
    price = model_prices.get(model, None)
    if price is not None:
        if isinstance(price, tuple):
            print(f"Model: {model}, Price per token (prompt): ${price[0]:.4f}, Price per token (completion): ${price[1]:.4f}")
        else:
            print(f"Model: {model}, Price per token: ${price:.4f}")
    else:
        print("Invalid model. Please choose a valid model.")