def get_clean_input(prompt: str = ''):
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
    try:
        int(value)
        return True
    except ValueError:
        return False