
#   Author:     Harry O'Malley
#   Date:       22/02/2022
#   File:       handler.py
#
#   Library to monitor a folder for changes
#   When a change is detected, the class state is modified to reflect this
#   The state must be monitored by the thread which instantiates this handler
#   An internal counter is kept to allow a main program to act differently every x executions

from watchdog.events import PatternMatchingEventHandler
from helpers import *
from datetime import datetime
from logger import logger


class Handler(PatternMatchingEventHandler):
    #   Handler class
    #   State:
    #       0 - nothing
    #       1 - file modified
    #       2 - file created/deleted
    state = 0
    modifications = 0
    last_changed = datetime.now()

    def __init__(self, patterns):
        PatternMatchingEventHandler.__init__(self, patterns=patterns,
                                             ignore_directories=True, case_sensitive=False)

    def resetState(self):
        logger.info("Resetting state")
        self.state = 0
        logger.info(f"Handler state: {self.state}")

    def resetMods(self):
        self.modifications = 0

    def on_modified(self, event):
        delta = datetime.now() - self.last_changed
        # debounce
        if(delta.total_seconds() < 0.5):
            return
        self.modifications += 1
        time = datetime.now().strftime("%H:%M:%S")
        logger.info(
            f'\t{self.modifications} - {time}: {event.src_path} was {blue("modified", True)}')
        # dont change if state is already file created
        self.last_changed = datetime.now()
        if(self.state == 0):
            self.state = 1

    def on_created(self, event):
        self.modifications += 1
        time = datetime.now().strftime("%H:%M:%S")
        logger.info(
            f'\t{time}: {event.src_path} was {purple("created", True)}')
        self.state = 2
    on_deleted = on_created
