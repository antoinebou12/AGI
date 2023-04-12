from datetime import datetime


def get_clean_input(prompt: str = ""):
    """
    Gets user input and handles KeyboardInterrupt gracefully.

    :param prompt: The prompt text to display before getting input.
    :return: The user input as a string.
    """
    try:
        return input(prompt)
    except KeyboardInterrupt:
        print("You interrupted Auto-GPT")
        print("Quitting...")
        exit(0)


def is_valid_int(value):
    """
    Checks if a value is a valid integer.
    """
    try:
        int(value)
        return True
    except ValueError:
        return False


def get_datetime():
    """Return the current date and time"""
    return "Current date and time: " + datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
