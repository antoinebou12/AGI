# -*- coding: utf-8 -*-
import threading
import time

from rich.console import Console
from rich.spinner import Spinner as RichSpinner


class Spinner:
    """A simple spinner class"""

    def __init__(self, message="Loading...", delay=0.1):
        """Initialize the spinner class"""
        self.delay = delay
        self.message = message
        self.running = False
        self.spinner_thread = None
        self.console = Console()

    def spin(self):
        """Spin the spinner"""
        with self.console.status(self.message, spinner=RichSpinner()) as status:
            while self.running:
                time.sleep(self.delay)

    def __enter__(self):
        """Start the spinner"""
        self.running = True
        self.spinner_thread = threading.Thread(target=self.spin)
        self.spinner_thread.start()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Stop the spinner"""
        self.running = False
        self.spinner_thread.join()
