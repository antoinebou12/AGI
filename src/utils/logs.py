import logging

from rich.console import Console


def configure_logging():
    logging.basicConfig(
        filename="log.txt",
        filemode="a",
        format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        level=logging.DEBUG,
    )
    return logging.getLogger("AGI")


def print_to_console(*args, **kwargs):
    console = Console()
    console.print(*args, **kwargs)
